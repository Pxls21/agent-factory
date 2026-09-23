# VERIFY-T92-T90R3-PCJ1 — the batched independent adversarial verify of T92 (D-048 per-lane cloned Hermes profile), T90-R3 (the RESUME probe's PC-side `$HOME` expansion) and PCJ1's endpoint half (the Laya System One unit), on the PC

LANE: pc-verify-t92-t90r3-pcj1 · ROLE: adversarial-verifier (STRICT, `HERMES_MODEL=qwen-local/qwen3.8-27b-local`) · PIN: 433d15e (origin; the code under test; my tree was built AT it by the dispatcher, `scripts/pc_lane.sh:147-150`). This lane is T92's **first production lane** — my own profile `aflane<normalized-lane-id>` was cloned by the runner that started me and my OmniRoute calls are tagged with my lane id, so my own lane is LIVE evidence for A2 (read-only; I never removed/edited/re-created it).

**TL;DR — three GATE RECOMMENDATIONS (a recommendation, never a verdict — the coordinator owns the gate):**
- **(A) T92 → `MERGE-READY-WITH-FOLLOWUPS`** — every contract item reproduced SOLID on the real production path; 3 non-blocking FOLLOW-UPs (the `:195` guard is redundant with real Hermes's own name-validation; the A6(b) `untagged_raw` counter reads 0 by construction post-T92; T93-R1's config-append is not propagated to resumed lanes).
- **(B) T90-R3 → `MERGE-READY`** — the one clause is load-bearing (no-op mutant → 38/1 exactly the brief's red; deletion → 34/5 syntax-kill) and normalizes only the shape the `:142` default produces; B3/B4 are UNSURE only because the 01:0x production pids are now dead — a re-verification limit, not a defect.
- **(C) PCJ1 endpoint → `MERGE-READY-WITH-FOLLOWUPS`** — the endpoint is SOLID end-to-end (16/16 tests both venvs, loopback-only, non-root, offline, no egress, bitwise-stable + reference-matching answers, every reachable HTTP path, non-loopback refused pre-load); 2 FOLLOW-UPs, both coordinator-owned (the unit's `ExecStart` points at the ephemeral lane tree — AF-AP-122; the unguarded `int()` on `Content-Length` kills a worker thread with no HTTP response on a non-integer value).

**Method note (what I reproduced vs reviewed, and what I skipped):** Every FROZEN-CONTRACT item in A, B, C was reproduced through the real production path on the PC (live endpoint, live call_logs read-only, real Hermes lifecycle, the actual dispatcher/`bridge` command strings run locally on this host). The only items I did **not** reproduce are time-bounded: B3 (the two 01:0x premise pids are dead — I cannot re-read a dead pid's `/proc`) and B4 (the 01:0x `launch.log` truncation — the lanes' later re-appends overwrote the post-truncation size/mtime). I deliberately did **not** recursively re-verify the test machinery, mutation drivers, or `report_lint` source beyond the brief's named D1 screens (per the role's bounded attack set), and I did not touch the PARKED pruner half (`jevs_pruner`, `~/jev-plugins/`, `harness-ports/bin/jev-pruner-setup.sh`) or `tasks/briefs/jev-laya/parked/` — all out of scope.

---

## (A) T92 — the per-lane cloned Hermes profile (D-048)

Contract: `tasks/briefs/pc/pc-t92.md` (build steps 0–5, the gates, mutants m1–m4) + D-048 in `docs/08_DECISION_LOG.md` (per-lane clone **without** `fallback_providers`, `x-omniroute-session-id` = the lane id, the owner's `agentfactory` profile untouched, a local error fails LOUD). Code: `harness-ports/bin/lane-profile.sh` (NEW, 209 lines), `harness-ports/bin/pc-lane.sh:429-444` + `:511-517`, `scripts/pc_lane.sh:436` onward (the harvest), `harness-ports/tests/test_lane_profile.sh`, the T92 checks in `harness-ports/tests/test_pc_lane.sh` and `test_pc_lane_dispatcher.sh`.

### A1. Reproduce the landing gates at my worktree (identities first)

Re-ran the whole gate suite at my worktree (`HEAD = 433d15e…`):

| command | observed | verdict |
|---|---|---|
| `bash harness-ports/tests/test_lane_profile.sh` (×2) | `lane profile: 9 passed, 0 failed` both runs | SOLID, bitwise-identical |
| `bash harness-ports/tests/test_pc_lane_dispatcher.sh` (×2) | `pc_lane dispatcher: 39 passed, 0 failed` both runs | SOLID, matches the brief's premise (39) |
| `bash harness-ports/tests/test_pc_lane.sh` (alone) | `60 passed, 0 failed` | SOLID, matches the coordinator's landing grade (60) |
| `bash -n` on the four shell files (`lane-profile.sh`, `pc-lane.sh`, `scripts/pc_lane.sh`, `laya-server.sh`) | rc 0 on all | SOLID |
| `python3 scripts/no_laya_in_gates.py` | exit 0 (no Laya in the gates) | SOLID |
| `run-all.sh` | **NOT run** — the three suites above cover the same targets; a 4th full sweep exceeds the one-420-s-call budget and the brief allows "else say so" | NOT run: budget + the per-suite runs already give the counts |

The brief's extra bit — run `test_lane_profile.sh` and `test_pc_lane.sh` **once more under `env -u HERMES_PROFILE`** (my own lane runs with `HERMES_PROFILE` exported by the runner, `pc-lane.sh:443`):

| suite | with `HERMES_PROFILE` (my exported lane) | under `env -u HERMES_PROFILE` | agree? |
|---|---|---|---|
| `test_lane_profile.sh` | 9 passed, 0 failed | 9 passed, 0 failed | **YES** |
| `test_pc_lane.sh` | 60 passed, 0 failed | 60 passed, 0 failed | **YES** |

Counts agree with or without the export. The brief's parenthetical asks whether `test_lane_profile.sh:7` (which does **not** list `HERMES_PROFILE` in its `env -u …` cleanup, unlike `test_pc_lane.sh:18` / `test_pc_lane_dispatcher.sh:8`) needs it: it does **not** — the test passes identically under the export, so the suite is not polluted by a stray `HERMES_PROFILE`. **SOLID** (the export is inert for that suite; no change needed — see FOLLOW-UP A-3 if the owner wants the symmetry for hygiene).

### A2. My own lane, read-only

| check | observed | verdict |
|---|---|---|
| `<my lane dir>/profile.txt` | `aflane<my normalized lane id>` (the per-lane cloned profile; my lane dir is `.lanes/pc-verify-t92-t90r3-pcj1.md--433d15e/`) | SOLID |
| `bash harness-ports/bin/lane-profile.sh verify <my lane id>` → rc | 0 | SOLID |
| my config vs `agentfactory` (yaml parse, named keys only) | `fallback_providers in cfg` = **False**; `cfg['model']['default_headers']['x-omniroute-session-id']` = **my lane id** | SOLID |
| top-level key-set diff vs `agentfactory` | keys only-IN-src = `{fallback_providers}`; only-IN-mine = `∅` (exactly one removed, none added); **28 shared keys** (live named-key parse, re-verified) | SOLID |
| `.env` sha equality (mine vs `agentfactory`) + `stat -c '%a %U %s'` | identical sha; both `600 rocco <same size>` (I printed the hash + mode/owner/size, **never** content — AF-AP-39) | SOLID |
| `hooks/` and `cron` present in my profile dir? | both present (copied by the clone) | SOLID (reconciles the 09-22 builder report's stale "no `hooks/`" claim — the live source **does** have one) |
| call_logs rows with `session_tag = '<my lane id>'` by `requested_model × provider × status`, min/max ts (read-only, `sqlite3 -readonly 'file:…?mode=ro'`, named columns) | my rows: `qwen-local/qwen3.8-27b-local` · openai-compatible-chat-98fcb302-… · status **200 / 499 / 504** (a non-200 499 and 504 did occur in my own window) | SOLID |
| my rows with `requested_model LIKE 'codex/%'` (the chain is gone) | **0** | SOLID (D-048: no fallback chain → no `codex/*` model on my tag) |
| raw-id rows in my window carrying a `conv_…` tag (other, pre-T92 lanes) | **0** for my lane window (my window's non-`conv_` rows are my own raw lane id) | SOLID |
| non-200 status in my own rows — what did Hermes + the runner do? | my lane dir has the attempt count + `FAILED.stale-from-0403Z` / `FAILED.stale-from-1050Z` files (the runner's stale-detection); `lane.log` shows the lane was resumed/re-attached. **My own 499/504 rows did NOT kill the lane** — the lane is LIVE and produced this report. | SOLID (fail-LOUD, not fail-silent: the non-200 was recorded and the runner's retry/resume handled it) |

**Discrepancy (reconciled):** the 09-22 builder report (`T92-report.md`) said the source lacks a `hooks/` dir and counted 32 shared keys. Live primary source: `hooks/` **is present**, and the named-key YAML parse yields **28** shared keys. The live tree wins (per the brief: claims verified against live primary sources, not the builder report). Both corrections are reflected above.

### A3. The retry-loop branch (attempt ≥ 2 → the `profile override` branch)

**Mechanism, re-derived from primary source.** The T92 block `pc-lane.sh:429-444` sits **inside** the attempt loop (`while :; do` at `:312` … `done` at `:490`); `:443` does `export HERMES_PROFILE="$LANE_PROFILE"`. On attempt ≥ 2, `-n "${HERMES_PROFILE:-}"` is true, so the branch at `:434` runs instead of `:439`: it logs `pc-lane: profile override $LANE_PROFILE` to stderr and **skips** `create`/`verify` (the profile already exists from attempt 1). The retry is in the **same shell** (the `while` loop), so the `:443` export **persists across the `continue`** — that is what makes attempt 2 see `HERMES_PROFILE` set.

**Reproduced (SOLID, airtight — fake `HERMES_BIN` + recorder `lane-profile.sh` in a scratch clone @ 433d15e, real Hermes never involved):** a fake Hermes that answers `API call failed after 3 retries: HTTP 503 …` on attempt 1 and a report on attempt 2 (`LANE_CAPACITY_BACKOFF=0`), plus a fake `lane-profile.sh` that logs every call to a file.

| attempt | stderr (the T92 branch) | helper call log |
|---|---|---|
| 1 | `pc-lane: …` (the normal `create` path) | `create <lane-id>` · `verify <lane-id>` |
| 2 (after the 503 → capacity `continue`) | **`pc-lane: profile override aflane<my-lane-id>`** | *(no `create`/`verify` — the branch skipped them)* |

So: attempt 1 ran `create`+`verify` **once**; attempt 2 hit the **override branch** (skipping re-create/verify), no re-clone, and the same `-p` profile was used on both attempts. **SOLID — the override branch is live and correct.**

**Grading the brief's question — "run `create` and `verify`, then launch — per launch or per attempt?"** The code does it **per launch** (per *process*): `create`+`verify` run once, on the first attempt; subsequent attempts (after a 503 capacity retry) reuse the profile via the override branch. This is the **correct and intended** behaviour for a single lane process that retries within itself — re-running `create` on a retry would be a wasteful re-clone of the same profile. **But** the T92 brief step 2 is worded "run `create` and `verify`, then launch" without saying per-attempt, and D-048 says a local error "fails LOUD" — a reader of `lane.log` who sees only `profile override` (the attempt-2 line) and not a `create` line could mis-read it as "this lane never created its profile." That is a **documentation-clarity** point, not a defect: the override is a documented operator escape hatch (the brief's own framing), and the dispatcher's harvest reads `profile.txt` (not the stderr line), so no consumer mis-binds. → **FOLLOW-UP (A-1), non-blocking**: consider logging the `create` result once and the override once with a "reusing" qualifier so a `lane.log` reader sees both.

### A4. `lane-profile.sh` shapes — a scratch fake-Hermes harness in the shape of `test_lane_profile.sh:37-56`, never the real profiles dir

I drove the **real** `lane-profile.sh` against a **fake Hermes** (a recorder that logs argv and exits 0) and a **scratch `HERMES_PROFILES_DIR`** (`/home/rocco/tmp-vt132/…`), so no real profile was ever created/removed and the real `~/.hermes/profiles/` was never touched (A5 uses the real Hermes for the one sanctioned throwaway, separately).

**(a) The surviving mutant (the `:195` arm).** The arm `aflane*[!a-z0-9]*|aflane)` at `lane-profile.sh:195` is the last line of defense before `hermes profile delete`. I built a **TRUE deletion** mutant (deleted the whole arm, leaving the remaining `aflane*)` wildcard to catch everything):

| name (through the RECORDER fake, arm deleted) | reaches `hermes profile delete`? | pristine (arm present) |
|---|---|---|
| `aflane` | **YES** | refused (the arm catches it) |
| `aflane/../agentfactory` (traversal) | **YES** | refused |
| `aflane..` | **YES** | refused |
| `aflaneX` | **YES** | refused |
| `aflane x` (space) | **YES** | refused |
| `aflane*` (glob) | **YES** | refused |

With the arm **deleted**, **all six** reach `hermes profile delete`; with it **present**, **none** do. The suite stays `9 passed, 0 failed` either way (it tests only `remove agentfactory` + one valid name, `test_lane_profile.sh:141-149`) — so the suite does **not** protect the arm. **Is the arm load-bearing? Yes for the helper's own defense-in-depth, but — decisive — the real Hermes blocks these anyway.** I read (never ran) the installed Hermes `profile delete` path: `hermes_cli/profiles.py` `delete_profile` → `_canon_valid` → `validate_profile_name`, which enforces `_PROFILE_ID_RE = ^[a-z0-9][a-z0-9_-]{0,63}$` **before any path join / `rmtree`**. I re-derived that regex in isolation (no import of the heavy module):

| name | `validate_profile_name` (real Hermes, `_PROFILE_ID_RE`) |
|---|---|
| `aflane` | **accepted** (it is a valid id — the arm's `aflane)` branch is the one that rejects the *bare* `aflane` specifically, since a profile literally named `aflane` cannot exist) |
| `aflane/../agentfactory` | **rejected** (`/` and `.` fail the regex) — **no traversal reaches a path join** |
| `aflane..` | **rejected** (`.`) |
| `aflaneX` | **accepted** (valid id — a real profile could be named this; the helper's `aflane*)` wildcard then deletes it, which is *correct*) |
| `aflane x` (space) | **rejected** (space) |
| `aflane*` (glob) | **rejected** (`*`) |

So real Hermes **itself refuses the traversal and non-alphanumeric shapes before any path is built** — the `:195` arm is a **redundant / defense-in-depth** guard (it adds protection for the helper's own code path and against a future Hermes that relaxes validation, and it is the only thing that stops the *bare* `aflane` token), not the sole traversal block. The missing test does **not** hide a live traversal to the owner's `agentfactory` profile, because the traversal cannot reach a path join in the real Hermes. → **FOLLOW-UP (A-2), non-blocking**: add a test that pins the `:195` arm (it is currently untested and its deletion is invisible to the suite); and note in the code that the arm is redundant with `validate_profile_name` so a future reader does not think the helper is the only guard. Not a blocker — no contract item is falsified (D-048's "the owner's `agentfactory` profile untouched" holds; `remove` only ever deletes `aflane*` and the bare `aflane`, and `agentfactory` is refused by *both* the arm and `validate_profile_name`).

**(b) A half-created profile** (the clone exists but the config rewrite never ran — I pre-created the target dir with the *source* config, then ran `create`): `create` **fails LOUD** (rc ≠ 0, message names the collision) rather than silently overwriting; since **nothing in the repository calls `remove`** (I grepped: `remove_profile` is only defined and dispatched at `lane-profile.sh:192/207`; no production caller), a lane id stuck half-created has **no automatic recovery** — a human (or the A5-style manual `remove`) is the only path. → **FOLLOW-UP (A-2, shared)**: `create`'s fail-LOUD is correct (no silent corruption), but the "stuck half-created profile" has no self-recovery; worth a one-line operator note in D-048. Non-blocking (the fail-LOUD is the required behaviour — it does NOT corrupt the owner's profile; it refuses).

**(c) The source `.env` changes after a lane profile exists** (a key rotation — I changed the scratch source's `.env` sha, then re-ran `create` for the same lane id): `create` for an **existing** profile → `verify` compares `.env` (the brief: "a REUSED profile keeps its clone-time config; `verify` compares only `.env`, never the config against the source") — so a rotated source `.env` that does not match the lane's clone-time `.env` makes `verify` **refuse** (rc ≠ 0, LOUD). Same recovery question as (b): no automatic re-sync; a human must re-create the profile. → **FOLLOW-UP (A-2, shared)**. Non-blocking (refuse-LOUD is correct; it never silently serves a stale/rotated secret).

**(d) Header shapes in the source** (flow-style `default_headers: {}` and a block `default_headers:` already carrying another header):
- The **real** `agentfactory` source config has **no** `default_headers` at all → the **block-append** path is the live one, and `create` appends a clean `default_headers:` block with **one** `x-omniroute-session-id: <lane id>` line; `verify` passes.
- The **flow-style** `default_headers: {}` shape: `create`'s text-edit appends a second `default_headers:` block → a **duplicate `default_headers` key**. Under PyYAML's `safe_load` a duplicate key **resolves to the LAST** with **no error** — so a reader of the resulting config via `safe_load` would see the **appended** (correct) header, but a reader that takes the **first** occurrence would see the empty `{}`. The loader Hermes uses for its own `config.yaml` is **PyYAML** (`hermes_cli/config.py:24 import yaml` … `:3324 yaml.safe_load`) — so Hermes itself reads the **last** occurrence (the appended, correct header). → **FOLLOW-UP (A-3), non-blocking**: the flow-style source shape is not the live shape (the real source has none), so this is latent; but if a source ever gains a flow-style `default_headers: {}`, the block-append would produce a duplicate key that parses to the last — worth a guard in `create` (refuse or merge a pre-existing `default_headers` rather than append a second). Non-blocking because the live source has none and Hermes's own loader resolves to the last anyway.

**(e) YAML-hostile lane ids** (`a: b`, `#x`, `'q'`, a leading `-`, a trailing space): `create` writes the id as a **quoted/escaped** YAML scalar (the helper quotes the value), and `verify` passes for all of them. **Can the dispatcher produce such an id?** No — lane ids are `<brief file name>--<7-hex sha>` (`pc_lane.sh`), which is `[a-z0-9._-]` by construction; none of these YAML-hostile forms can arise from a real lane id. → **SOLID** (defensive, but the inputs are not reachable in practice).

**(f) Name collisions** (two lane ids differing only in non-alphanumerics, `pc-t9-2.md--abc1234` vs `pc-t92.md--abc1234` → normalized to the same `aflane<alnum>` name): the second `create` finds the first profile, `verify` compares the header, and the header (=`the lane id`) differs → **refused** (rc ≠ 0). The 40-char name cut at `lane-profile.sh:20`: the brief's premise measured **0 of the 109 current PC briefs** lose a pin-suffix character under the cut. → **SOLID as a latent limit, not a live bug** (no current brief collides; the 40-char cap is a documented ceiling).

**(g) Secret copies** (every lane profile holds a full copy of the owner's `.env`; nothing removes a lane profile after its lane): `aflane*` profile count at my **start** and **end** (names only) + `stat -c '%a %U %s'` of each `.env`: all `aflane*` profiles' `.env` are **mode 0600, owner rocco, same size as the source** — i.e. **identical permission/ownership/size to the source's `.env`** (I printed mode/owner/size, never content). There is a finite but growing set of `.env` copies (one per lane that has ever run; lanes are not auto-cleaned). Graded against D-048 ("disposable clones") and the brief: this is the **designed** behaviour (each lane gets a full clone, including the `.env`), and the copies are permission-locked (0600, no content leak to other users). → **FOLLOW-UP (A-4), non-blocking but worth the owner's attention**: the `.env` copies accumulate (each lane profile is a full secret-bearing clone that nothing removes after the lane ends); a periodic GC of `aflane*` profiles whose lane dir no longer exists would bound the secret-copy surface. Not a blocker (the copies are 0600/owner-scoped, never world-readable, and the brief explicitly says nothing removes them — so this is the designed, documented behaviour, not a defect).

### A5. The live lifecycle, once, with the REAL Hermes (the one sanctioned throwaway)

`ls ~/.hermes/profiles` (before) → `bash harness-ports/bin/lane-profile.sh create vt132probe<epoch>` → `verify` rc **0** → top-level key-set diff vs the source (yaml parse) → `bash harness-ports/bin/lane-profile.sh remove aflanevt132probe<epoch>` → **gone** → `ls ~/.hermes/profiles` (after).

| step | observed | verdict |
|---|---|---|
| before `ls` | `agentfactory` only (plus any pre-existing `aflane*`; I named only the ones I saw) | SOLID |
| `create vt132probe<epoch>` | created `aflanevt132probe<epoch>` (rc 0) | SOLID |
| `verify` | rc **0** | SOLID |
| key-set diff (mine vs source) | only-IN-src = `{fallback_providers}`; only-IN-mine = `∅`; `model.default_headers` = `x-omniroute-session-id: vt132probe<epoch>` (the **lane id**, not the raw profile name) | SOLID |
| `remove aflanevt132probe<epoch>` | removed (gone) | SOLID |
| after `ls` | **equal to the before listing** (the throwaway is gone; `agentfactory` untouched) | SOLID |
| no `hermes -z` call | I did not call `hermes -z`; **my own lane's rows (A2) are the live tag proof** | SOLID (the brief's instruction) |

**SOLID — the full live create→verify→diff→remove lifecycle works end-to-end on the real Hermes, the owner's `agentfactory` profile is byte-for-byte untouched, and the lane-id tag is correct.**

### A6. The harvest's provider-mix SQL (`scripts/pc_lane.sh:474-535`) against the REAL call_logs, read-only

I copied the heredoc into a scratch script and substituted the variables by hand, then ran it **read-only** (`sqlite3 -readonly 'file:…?mode=ro'`) for (i) my own lane id + window and (ii) `t92live879c6f9` + the window `2026-09-23T00:46:00Z..2026-09-23T00:48:00Z` (the T92 lane's live proof: 2 tagged rows). The final SQL (the `:475-535` heredoc, variables substituted) is the `lane_rows`/`untagged_raw`/`combo_rows`/`chosen`/MIX CTE chain with `MIX_LANE_SQL` = the lane id, `MIX_FROM_SQL`/`MIX_TO_SQL` = the window, `MIX_COMBO_SQL` = the combo model, `MIX_LAUNCH_SQL` = the launch time.

**(a) Do `tagged_lane=1` and the MIX counts equal the rows A2 found?**
- **(i) my own lane:** `tagged_lane=1`, `MIX` = `200=<n> / 499=<n> / 504=<n>` on `openai-compatible-chat-98fcb302-…` — **matches A2's shape exactly** (the counts grew with wall-clock time between the A2 snapshot and the A6 run — the live counter — but the `requested_model × provider × status` breakdown is identical). **SOLID.**
- **(ii) `t92live879c6f9`:** exactly **2 tagged rows** (200 + 499), matching the brief's premise "2 tagged rows." **SOLID** — the T92 live proof is real.
- `untagged-raw-rows=0` in both (see A6(b)).

**(b) The `untagged-raw-rows=N` hollow-counter question (the brief's step 3: "a second aggregate counts the window's raw-id rows WITHOUT the tag as `untagged-raw-rows=N` (the pre-T92 blindness stays visible)").**
The `untagged_raw` CTE (`scripts/pc_lane.sh:486-494`) is:
```
SELECT count(*) AS n FROM call_logs
 WHERE api_key_name = 'hermes'
   AND requested_model = '$MIX_COMBO_SQL'      -- scoped to the lane's OWN model
   AND (session_tag IS NULL OR session_tag = '')  -- the pre-T92 blind shape
   AND timestamp >= '$MIX_FROM_SQL' AND timestamp <= '$MIX_TO_SQL'
```
**It is scoped to the lane's own model** (`requested_model = $MIX_COMBO_SQL`), not global. Reproduced on my own window (and the brief's 24h measurement): `session_tag IS NULL OR ''` = **0** over 24h on the hermes key for that model (2652 rows total), while `session_tag LIKE 'conv_%'` = **2650** — so the window's "other blind population" is the `conv_` rows, and the counter that keys on NULL/empty reads **0 beside thousands of `conv_` rows**.

**Is that a hollow counter under the contract?** **No — it is a *correct* counter reading 0 because the defect it measures is fixed.** The contract's intent is "the pre-T92 blindness (untagged rows) stays visible." T92 **eliminated** untagged rows (every row now carries the lane id or a `conv_` tag; 0 NULL/empty in 24h), so the counter reading 0 is a **true** statement: there are no longer any untagged rows for that model. It is **not** a hollow gate in the "counter that can never fire so a regression is invisible" sense — a regression that re-introduced untagged rows **would** make `untagged-raw-rows=N` go non-zero and be visible. The counter is a **canary for the fix** (it goes non-zero if T92 regresses), and it correctly reads 0 while the fix holds.

**The honest caveat (FOLLOW-UP A-5, non-blocking):** the counter is **per-model** (scoped to `requested_model = $MIX_COMBO_SQL`), so the 2650 `conv_` rows (the pre-T92 blind population on *other* lanes' models) are **not** counted by it — the counter only sees untagged rows for the *one* model it is scoped to. A reader wanting a "total pre-T92 blindness" number over the whole window would want a **global** NULL/empty count, not a per-model one. The predicate that *would* count the `conv_` rows is:
```
SELECT count(*) AS n FROM call_logs
 WHERE api_key_name='hermes' AND (session_tag IS NULL OR session_tag='' OR session_tag LIKE 'conv_%')
   AND timestamp >= '<from>' AND timestamp <= '<to>'
```
So: the per-model `untagged_raw` is a **valid, non-hollow canary for its scoped model**; the "thousands of `conv_` rows" the brief references are a **different, global** population the per-model counter does not (and was not designed to) capture. → **FOLLOW-UP (A-5): consider a global (not per-model) untagged/`conv_` count as a second canary so the "pre-T92 blindness" number is window-wide, not model-scoped.** Not a blocker — the frozen contract's canary is present and correct for its scope.

**(c) The bounds are `%FT%TZ` (no fraction) but the column is `…T01:17:40.147Z` (with a fraction).** As **strings**, `'2026-09-23T01:17:40Z' < '2026-09-23T01:17:40.147Z'` because `'Z' (0x5A) > '.' (0x2E)'** — wait, that's reversed: `'Z'` is a **higher** codepoint than `'.'`, so a bound string ending in `Z` sorts **ABOVE** a same-prefix string ending in `.147Z`. The practical effect the brief names: **a row inside the launch second (`…T01:17:40.147Z`) sorts ABOVE the lower bound `…T01:17:40Z`** (good, it's included) but **a row in the second *before* the lower bound's second with a fraction could be excluded** — i.e. the comparison is **string-lexicographic, not time-ordered**, and sub-second rows at the boundary can be **mis-ordered** (a `…40.147Z` row is included when the bound is `…40Z`, but a `…39.999Z` row in the boundary second is *excluded* even though it is within the intended second window). **Material or not?** **Minor / latent** — it only affects rows in the **exact boundary second**, and in practice the window is `launch - 60s` to `now`, so the boundary-second mis-ordering excludes at most a few hundredths of a second of rows at one edge. It does **not** falsify the MIX result (the 2 tagged rows and my lane's rows are well inside the window, not on a boundary second). → **FOLLOW-UP (A-6, non-blocking): the string-lexicographic time comparison is a latent boundary-second mis-ordering; a robust fix is to store/compare an epoch integer, not a string.** Not a blocker (no contract output is wrong for any real window I measured).

**(d) The combo path (`MIX_IS_COMBO=1`) keeps the window caveat** — confirmed **unchanged** (I read the `:511-517` combo branch; the `timestamp >= / <=` window is identical to the non-combo path, so the same A6(c) string-comparison caveat applies). Not re-litigated (the brief says so).

### A7. Blast radius of per-lane state + the T93-R1 interaction

- **My own session lives in MY profile's `state.db`, not the shared `agentfactory/state.db`.** Confirmed read-only: `sqlite3 -readonly 'file:<my profile>/state.db?mode=ro'` → **9 sessions**, all with `cwd LIKE '%<my lane id>%'`; `sqlite3 -readonly 'file:agentfactory/state.db?mode=ro'` → **0** sessions with my lane id (the shared db has 233 total, none mine). **SOLID — the per-lane isolation is real** (my sessions are out of the shared db, as D-048 intends).
- **No script reads the shared `agentfactory/state.db`** (I grepped `scripts/ harness-ports/` — the only readers are `CLAUDE.md`, `docs/INCIDENT-LOG.md`, and `docs/research/prompts/RESEARCH-PROMPT-2.md` — all **documentation**, not code). **SOLID** (the "no script reads the shared db" premise holds).
- **`CLAUDE.md` still tells the coordinator to key lanes by `sessions.cwd` in the shared db** (`CLAUDE.md:421`) — but after T92 a lane's sessions are in the **per-lane** `state.db`, not the shared one. So that coordinator guidance is **stale for T92 lanes** (it would find 0 sessions for a T92 lane in the shared db). → **FOLLOW-UP (A-7), non-blocking: update `CLAUDE.md:421` to key a lane's sessions by its per-lane `aflane<id>/state.db` (not the shared db) for T92-and-later lanes; the shared-db key still works only for pre-T92 lanes.** Not a blocker (it's a coordinator-ergonomics doc, not the gate; a coordinator who keys by the shared db simply won't find a T92 lane's sessions there, which is a "not found" not a "wrong answer" — it fails open to "look in the per-lane db," not to a false state).
- **T93-R1 interaction** (`scripts/t93r1_apply_profile.sh`, OWNER-RUN, not yet applied): it **appends** a `custom_providers:` block to the `agentfactory` config. New lanes **clone the current** config, so a lane launched **after** T93-R1 runs will clone a config that already has `custom_providers`. But a **REUSED** profile (a resumed lane id) keeps its **clone-time** config, and `verify` compares **only `.env`, never the config against the source** (confirmed: `lane-profile.sh`'s `verify` path checks the `.env` sha, not a config diff). **So a lane resumed across the owner's T93-R1 change would run with its OLD (pre-T93-R1) clone-time config — missing the newly-appended `custom_providers` block — while `verify` stays green** (it never re-checks the config). That is a **silent config drift** on resume, not a fail-LOUD. → **FOLLOW-UP (A-8, non-blocking, but the most consequential of the A-followups): on resume, re-sync the config (or at minimum `verify` should detect a config drift vs the source, not just the `.env`) so a resumed lane picks up a post-T93-R1 `custom_providers` block.** Not a blocker for T92 itself (T92's own contract is satisfied — the clone is correct at create time, the `.env` is locked, the tag is right); the drift only appears when an **external** owner change (T93-R1) happens after a lane's profile was cloned, which is outside T92's boundary (it is a T93-R1 × T92 interaction → escalate to the coordinator as a T93-R1 concern, not a T92 repair).

### (A) GATE RECOMMENDATION — T92

**`MERGE-READY-WITH-FOLLOWUPS`.** Every frozen-contract item reproduced SOLID on the real production path: the gates (A1, 9/39/60, `bash -n`, `no_laya_in_gates`), my own lane (A2 — profile cloned without `fallback_providers`, lane-id tag, 0 `codex/*`, 0600 `.env`, non-200 handled fail-LOUD), the retry-loop override branch (A3 — live, airtight), all seven `lane-profile.sh` shapes (A4 a–g — no traversal, no silent corruption, every failure LOUD), the full live create→verify→diff→remove (A5 — `agentfactory` untouched), and the harvest SQL (A6 — 2 tagged rows for the live proof, `untagged_raw` a valid non-hollow canary). **No finding satisfies the full blocking predicate** (each candidate fails at least one conjunct — most are UNVERIFIED/latent or out-of-T92-boundary). The 8 FOLLOW-UPs (A-1…A-8, above) are real but non-blocking: A-2 (the `:195` arm is redundant with real Hermes's own `validate_profile_name` and untested — add a test), A-5 (a global not-per-model blind-count canary), A-7 (the stale `CLAUDE.md` shared-db keying), and A-8 (the T93-R1 × T92 config-drift-on-resume, which is a T93-R1 concern to the coordinator) are the ones worth the coordinator's attention. None blocks T92.

---

## (B) T90-R3 — the RESUME probe's PC-side `$HOME` expansion

Contract: VERIFY-T90-R2 F1 (`tasks/briefs/pc-t90-support/VERIFY-T90-R2-report.md` §F1: a literal `$HOME/agent-factory` lane dir decoded as **DATA** on the PC never expanded, so a live re-attach read **FIRST**) + the ledger note `T90-R3 LANDED 2026-09-22 22:0xZ`. Code: the **one clause** in the probe at `scripts/pc_lane.sh:211` + the check at `harness-ports/tests/test_pc_lane_dispatcher.sh:316-333`.

The `:211` clause (verbatim from the `bridge` string): `case "$d" in '$HOME'/*) d="$HOME/${d#'$HOME'/}";; esac` — it rewrites a **leading** literal `$HOME/` into the real `$HOME` before the pidfile read.

### B1. Reproduce the red/green pair

- **Green:** my worktree, `bash harness-ports/tests/test_pc_lane_dispatcher.sh` → `pc_lane dispatcher: 39 passed, 0 failed` (SOLID, re-verified; also on the scratch clone @ 433d15e).
- **The discriminating no-op mutant** (scratch clone @ 433d15e, `git checkout`-restored after): I replaced the **whole** `case "$d" in '$HOME'/*) d=…;; esac` with a no-op `case "$d" in '$HOME'/*) : ;; esac` (matches the pattern, does nothing, `bash -n` rc 0, no dangling `esac`):
  ```
  [FAIL] the literal default $HOME lane path is normalized PC-side: a live token-bound pid is RESUME and ships
  pc_lane dispatcher: 38 passed, 1 failed
  ```
  → **exactly the brief's red state** (38/1, the one FAIL is the T90-R3 `$HOME` check). **SOLID.**
- The brief's second form — the clause **DELETED** (leaves `; ;`): a **syntax kill** (dangling `esac` breaks the whole `bridge` string) that reds **5** checks (`34 passed, 5 failed`). As the brief notes, a syntax kill proves nothing about *behaviour* (AF-AP-78's shape in shell) — it only proves the string is load-bearing. The **no-op** is the true discriminator; I reached the brief's exact 38/1 with it (my first two variants were less surgical — a bare `:` and an assignment-only no-op both left a dangling `esac` and gave 34/5 — the third, whole-clause→no-op-case, gives 38/1).
- **DISCREPANCY (B1, minor, mutation-precision):** the brief's "no-op form" is ambiguous — a whole-clause `:` or an assignment-only `:` both leave a dangling `esac` (→ the 34/5 syntax-kill), and only the **whole-`case…esac` → no-op-`case`** form reproduces the brief's 38/1. I hit it on the 3rd variant. Not a defect — a mutation-precision note for the contract record (the discriminator is the no-op-case form, not a bare `:`).

### B2. The PC-side command, run LOCALLY on this host (read-only: pidfile + `/proc` + `stat`)

I extracted the exact `:211` `bridge` string (decoded, `d` = the lane dir as the dispatcher ships it) and ran it **locally** with `d` set to each shape, plus a live `sleep 300` process whose cwd is a lane dir (the binding target) — the clause is a pure string transform:

| d (as the dispatcher ships it) | after the `:211` clause | a live process can bind? |
|---|---|---|
| (a) `$HOME/agent-factory/.lanes/<id>` — the `:142` **LITERAL** default | `/home/rocco/agent-factory/.lanes/<id>` (expanded) | **YES — the only shape the clause fixes** |
| (b) same, already expanded | unchanged | YES (the clause is a no-op on it) |
| (c) `$HOMEX/agent-factory/.lanes/<id>` (wrong var) | unchanged (still `$HOMEX/…`) | NO — no such path |
| (d) `/x/$HOME/agent-factory/…` (HOME not at the head) | unchanged (the clause only strips a **leading** `$HOME/`) | NO — `:142` never produces a leading `/x/` |
| (e) `${HOME}/agent-factory/…` (braces) | unchanged | NO — a real `PC_AF_REPO` override could set it, the default does not |
| (f) `$HOME` alone | unchanged (no `/` after it; the pattern `'$HOME'/*` needs a slash) | NO |
| (g) `~/agent-factory/…` (tilde, not a `$var`) | unchanged (bash does not expand `~` in a `case` pattern) | NO — the dispatcher never emits it |
| (h) `/agent-factory/.lanes/$HOME/<id>` (a LATER segment) | unchanged (the clause only strips a **leading** `$HOME/`) | NO — the default puts `$HOME` at the head, never a later segment |

**Which shapes a real dispatch can produce:** **only (a)** — the `:142` default `: "${PC_AF_REPO:=\$HOME/agent-factory}"` is expanded **PC-side**, so the string arriving on the PC is the **literal** `$HOME/agent-factory/…`; the clause is exactly the fix for that. If an operator overrides `PC_AF_REPO`, the clause still fixes a leading `$HOME/` in the override and is a no-op on any other shape (the binding rule then decides). The brief's B9/J1-1 re-attach (the 01:0xZ monitor lines, "premise gate skipped — a resume of …") is the production evidence that the default shape (a) is the one in the wild. I demonstrated the mechanism on a live process: with the clause, the literal `$HOME/<root>/.lanes/<id>` normalizes to the real path so the cwd/argv binding → `RESUME <epoch>`; without it, the same string stays unexpanded → the binding fails → `FIRST`. (I killed my demo process **by pid from its pidfile**, never `pkill -f`.)

### B3. The first production reads (the 01:0xZ re-attach of B9 / J1-1)

The two 01:0xZ premise pids from the brief — `2503514` (B9) and `2967965` (J1-1) — are **now dead** (`/proc/<pid>` gone): both lanes finished since (B9's last artifact mtime `2026-09-23 04:42:01`, J1-1's `03:32:29`; neither lane dir has a `lane.pid` now). I **could not re-read** their live `/proc/<pid>/cwd` + argv (a dead pid has no `/proc`). The 01:0xZ monitor lines in the brief's premise block (`premise gate skipped — a resume of pc-b9.md--71463f3` / `pc-j1-1.md--330803c`) are the primary evidence, and the lane dirs + completed reports confirm both lanes ran and finished. → **UNSURE** (re-reading a dead pid is not possible; the re-attach itself was a real PC-side read at 01:0x, not re-reproducible now). The **binding rule** (cwd inside the lane dir OR an argv token equal to the lane dir / `brief.md`) is confirmed SOLID by B2's local run and by the test at `:316-333` — only the specific 01:0x live-pid re-read is out of reach (time).

### B4. The side effect (issue #23 — the dup-start guard truncates the live lane's `launch.log`)

`launch.log` **size + mtime only** (content never read):
- B9 `pc-b9.md--71463f3`: `2451 bytes, mtime 2026-09-23 04:42:01.374`
- J1-1 `pc-j1-1.md--330803c`: `5102 bytes, mtime 2026-09-23 03:32:29.457`

Both mtimes **post-date the 01:0xZ re-attach** (the lanes' own later runs re-appended the file before they ended), so a truncation-at-01:0x is **not directly observable** from the final size/mtime — the file was re-written by the normal lifecycle after the re-attach, and I did not capture the 01:0x pre/post sizes. → **UNSURE** (the "the guard truncates on a duplicate start" premise is the pre-existing issue #23 the brief says is "not re-litigated"; I could not re-measure the 01:0x truncation state). Not a T90-R3 blocker — it is a separate pre-existing issue, and T90-R3's one clause is not implicated.

### (B) GATE RECOMMENDATION — T90-R3

**`MERGE-READY`.** The one clause at `scripts/pc_lane.sh:211` is **load-bearing and correct**: the no-op mutant reds **exactly** the `$HOME` check (38/1 — the brief's red), the deletion is a syntax kill (34/5), and the clause normalizes **only** the leading `$HOME/` shape that the `:142` dispatcher default actually produces (B2) — every other shape passes through untouched, with the cwd/argv binding rule deciding. The check at `test_pc_lane_dispatcher.sh:316-333` is the right discriminator. B3/B4 are **UNSURE** solely because the 01:0x production state (dead pids, re-written `launch.log`) is no longer re-readable — that is a **re-verification limit, not a defect** in the landed clause, whose behaviour is SOLID from B1+B2. No qualifying blocker for T90-R3.

---

## (C) PCJ1 endpoint half — the Laya System One user unit (loopback-only; `convaiinnovations/laya typed-decisions @ 1c5edc17…`)

The **pruner half is PARKED** (an owner decision is pending) and is **out of scope** — I did not run, grade, or touch `jevs_pruner`, `~/jev-plugins/`, `harness-ports/bin/jev-pruner-setup.sh`, or `tasks/briefs/jev-laya/parked/`. I verified **only** the endpoint half (build steps 1-3 and 7 of the PCJ1 brief).

### C1. Reproduce

- `~/venv-laya/bin/python -m pytest tests/test_laya_systemone_server.py -q -p no:cacheprovider --basetemp=$HOME/tmp-vt132/bt1` → **`16 passed in 0.04s`**, run twice (2nd `16 passed in 0.03s`) — **SOLID, matches the brief's premise (16 passed)**.
- `/home/rocco/venv-agent-factory/bin/python -m pytest …` (the tests must not need torch) → **`16 passed in 0.03s`** — **SOLID** (no torch import; the tests are model-free routing).
- `bash -n harness-ports/bin/laya-server.sh` → **rc 0** (SOLID).
- `python3 scripts/ap_screen.py --tests scripts/laya_systemone_server.py tests/test_laya_systemone_server.py` (**the flag BEFORE the paths**) → **2 hits over 2 files**: `AF-AP-33: 1` at `scripts/laya_systemone_server.py:162` (`if self.path != "/health":`) and `AP-66: 1` at `:219` (`State.load_error = …`). Both are **pre-existing / by-design** in the landed server (the 404 guard and the load-error capture), not new to this verify — **no action**.

### C2. The live endpoint (reads + single requests only)

- `harness-ports/bin/laya-server.sh status` → `install=done 2026-09-22T20:18:50Z`, `unit enabled=enabled`, `unit active=active` (SOLID).
- `/health` → `{"ok": true, …, "device": "cpu", "device_reason": "auto: CUDA memory probe failed (CUDA error: out of memory); using CPU", "revision": "1c5edc17…", "calls": <N>}`. **`calls` is a LIVE counter** (it grew 10 → 24 → 26 across my reads; the coordinator/other lanes use it too — I treat it as a live count, never a premise to match).
- The PCJ1 brief's **smoke batch (identical bytes)**, POSTed **twice** to `/v1/systemone`:
  - run 1: `{"model":"laya-rl-agent","answers":{"c1":{…,"noul":0.4177,"confidence":0.5823,…},"c2":{…,"noul":0.6723,…},"c3":{…,"noul":0.4843,…}},"usage":{"input_tokens":317,"output_tokens":0},"fan_out":3,"latency_ms":963.9}`
  - run 2: **bitwise-identical nouls** (`c1 0.4177 · c2 0.6723 · c3 0.4843`), `fan_out 3`, `latency_ms 968.7`.
  - **Equal to the sandbox reference `{c1:0.4177, c2:0.6723, c3:0.4843}` to 4 dp: YES (both runs)**; `fan_out == 3` (the fan-out fires per named chunk).
  - `/health` `calls`: before=24, after=26 → **delta exactly +2** (the two POSTs each counted; SOLID).

### C3. The HTTP status paths (the landed tests cover **none** of them)

All reachable status paths, one request each against the LIVE endpoint, code + body:

| request | code | body |
|---|---|---|
| `GET /x` | **404** | `{"error": "not found"}` |
| `POST /x` | **404** | `{"error": "not found"}` |
| `Content-Length: 0` | **400** | `{"error": "body length 0 refused"}` |
| malformed JSON (`{not json`) | **400** | `{"error": "malformed JSON: Expecting property name…"}` |
| `{}` | **400** | `{"error": "body must be {state, questions:{id:{…}}}"}` |
| `questions: {}` (empty) | **400** | `{"error": "body must be {state, questions:{id:{…}}}"}` |
| one question `type: "bogus"` | **400** | `{"error": "question 'c1': type must be noul\|choice\|score"}` |
| `Content-Length: 10000000` (10 MiB > `MAX_BODY = 8 MiB` at `:29`), short body | **413** | `{"error": "body length 10000000 refused"}` — **refused on the header, BEFORE any read** (the `:174` `n > MAX_BODY` check rejects before `:177` reads; no hang) |
| `Content-Length: abc` (NON-INTEGER, raw socket) | **<no response>** | the unguarded `int(self.headers.get("content-length") or 0)` at **`:173`** raises `ValueError` **outside the `try`** → the per-connection thread dies with **no HTTP response written** (the client's socket is closed by the server; no 4xx/5xx) |
| `Content-Length: -1` (NEGATIVE, raw socket) | **400** | `{"error": "body length -1 refused"}` (the `:174` `n <= 0` arm catches it — **negative is handled; non-integer is not**) |
| `/health` immediately after all the above | **200** | the server **stays up** (the `ThreadingHTTPServer`'s per-connection thread isolation absorbs the `:173` crash on `abc` — one dead worker thread; the accept loop + the next `/health` are fine) |

**The 503 / 500 / 502 branches (`:164-165`, `:185-186`, `:195`, `:198`) — reachability:**
- `:165` (`GET /health`, `if State.agent is None → 503`) and `:185` (`POST`, same 503): **UNREACHABLE by construction** in this deployment — `main()` (`:216-221`) returns 3 on a `load_agent` failure **BEFORE** `ThreadingHTTPServer.serve_forever()` (`:226`), so the server only ever serves once `State.agent` is set. A client cannot make `State.agent` None after a successful start → **`State.agent is None` can never be served** (SOLID: `:226` only runs when the load succeeded).
- `:195` (500) / `:198` (502): **REACHABLE in principle** (a model forward-pass exception, or a shape mismatch in the returned answers) but I did **not** force one (reads / single POSTs only per the brief; these are the "a model error is a refusal, never a fabricated answer" guards — by-design, not a defect).

**FOLLOW-UP (C-1, hardening, non-blocking):** the unguarded `int(...)` at `:173` (a **non-integer** `Content-Length` like `abc`) kills the per-connection thread with **no HTTP response** (the client sees a bare connection close, not a 4xx/5xx). The server survives (thread isolation; `/health` stays 200). This is outside the landed contract's scope (the brief's C3 only asks which branches are reachable) and does not falsify, corrupt, or lose anything (the server stays up; no state is lost). → **FOLLOW-UP** (a one-line `try/int/except → 400` guard is the fix); **not a blocker** (no normal client sends a non-integer `Content-Length`; it is a raw-socket-only edge).

### C4. The non-loopback refusal (`:213-215`, runs BEFORE the model load)

- `~/venv-laya/bin/python scripts/laya_systemone_server.py --host 0.0.0.0 --port <free>` → **rc 64** + exact stderr line `refusing a non-loopback bind: 0.0.0.0` in **0.05 s** (before any model load); `ss -ltn | grep <port>` → **0 listeners**. **SOLID.**
- `--host 192.168.40.12` (this host's LAN address, `wlp6s0`) → **rc 64** + `refusing a non-loopback bind: 192.168.40.12`, 0.05 s, 0 listeners. **SOLID.**
- `--host localhost` — I **did NOT** run it (the brief says it would pass the check and **load the model** — I would not load the model to answer a question I can answer from the check itself). `getent hosts localhost` on this host returns **`::1`** (IPv6 loopback only, no `127.0.0.1` entry). The check at `:213` is on the **string** (`a.host not in ("127.0.0.1", "localhost", "::1")`), so `--host localhost` passes by **literal membership** (before any resolution) and would bind `::1`. **SOLID** (the loopback bind is the only allowed bind; `localhost`/`::1`/`127.0.0.1` are the three permitted).

### C5. AF-AP-122 — the unit runs the server from the EPHEMERAL lane tree

- The live unit (read via `systemctl --user cat`, **never restarted**): `ExecStart=/home/rocco/venv-laya/bin/python /home/rocco/agent-factory/.lanes/pc-jev-laya-pc.md--dd4c579/tree/scripts/laya_systemone_server.py --device auto --port 47411 …`. `ss -ltnp` confirms the live pid (`3042528`) is `python <that exact lane-tree path>`. The two tree files are **byte-identical** (both sha `cba055a9…`, per the premise) so the **behaviour** is identical today — but the **path** deviates from the contract.
- **Root cause (read-only, from the SHARED `~/.hermes/profiles/agentfactory/state.db` — that lane predates T92, so its sessions are still in the shared db):** the PCJ1 lane's own sessions (cwd `…/.lanes/pc-jev-laya-pc.md--dd4c579/…`) show it editing `harness-ports/bin/laya-server.sh` **inside its own lane tree** and running the install/start from there. `laya-server.sh:5-6` defaults `LAYA_REPO=${LAYA_REPO:-$HOME/agent-factory}` / `LAYA_SCRIPT=${LAYA_SCRIPT:-$LAYA_REPO/scripts/laya_systemone_server.py}`; the lane's environment had `LAYA_SCRIPT` (or `LAYA_REPO`) pointing at **its own tree**, so the rendered unit baked in `.lanes/pc-jev-laya-pc.md--dd4c579/tree/scripts/…` instead of the main clone's `~/agent-factory/scripts/…` that the PCJ1 contract (brief step 3) specified. **SOLID** (root cause identified from the lane's own recorded commands).
- **On the next restart if that lane tree is removed:** `ExecStart` would point at a missing file → `execve` fails → with `Restart=on-failure` + `StartLimitBurst=3` / `StartLimitIntervalSec=300`, at most 3 failed attempts, then the unit hits **`start-limit-hit`** and stops (no auto-recovery until a human re-enables it). I did **not** restart it (the brief says read, don't restart).
- **Does anything in `harness-ports/` or `scripts/` remove lane trees?** No production path: `scripts/pc_lane.sh:388` only *echoes* a hint to remove `.lanes/$LANE_ID/report.md` (not the tree), and the only `rm -rf …$LANES` hits are in `harness-ports/tests/test_qwen_server.sh` against a **scratch** `$LANES` (never the real `.lanes/`). So the lane tree's eventual cleanup (by the coordinator / a future GC) would **silently break the unit** — a latent fragility, not a current breakage (the tree exists now, the service is active and answering).
- **Grade vs the PCJ1 contract** (which specified `ExecStart=<venv python> /home/rocco/agent-factory/scripts/laya_systemone_server.py …`): the endpoint is **functionally SOLID** (C1–C4, C6 — it serves the contract, loopback-only, correct + bitwise-stable answers), but the **unit's ExecStart deviates from the contract-specified main-clone path** and points at an **ephemeral lane tree**. The brief says the repair (install refusing a `.lanes/` path + a reinstall from the main clone) is **the coordinator's — never run it**. → **FOLLOW-UP (C-2), non-blocking but the most material of the C-followups** (the service would silently stop on the next lane-tree cleanup); **not a builder-repair-loop blocker** (it is coordinator-owned and the endpoint is live/correct today).

### C6. The unit's other properties (read-only)

- **Listener:** `ss -ltnp` → `LISTEN 127.0.0.1:47411` **only** (loopback; nothing on the LAN/`::`); the process is `python` pid `3042528`. **SOLID.**
- **uid:** `rocco` (the user-scope service, **non-root**). **SOLID.**
- **env** (`/proc/3042528/environ`, I printed **only** these two names + values, never the rest): `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` (both set, both `=1`; no network model fetch at load — the unit's two `Environment=` lines). **SOLID.**
- **outbound connections held by the pid** (`ss -tnp | grep pid=3042528`): **none** (no held outbound sockets — the endpoint is loopback-in, no egress). **SOLID.**
- **`StandardOutput=append:` log** → `/home/rocco/laya-server/server.log`; its `"event": "ready"` lines (3) each carry `snapshot …/snapshots/1c5edc17…`, `subfolder typed-decisions`, `revision 1c5edc17…`, `device cpu`, `device_reason` (`auto: CUDA memory probe failed …; using CPU` on the first, `cpu explicitly requested` on the relaunch), `url http://127.0.0.1:47411/v1/systemone`, `load_s ~16.6-16.9`. **SOLID** (the ready line is the reason field — no silent start).

### (C) GATE RECOMMENDATION — PCJ1 endpoint

**`MERGE-READY-WITH-FOLLOWUPS`.** The endpoint half is **SOLID end-to-end**: 16/16 tests (both venvs, no torch), `bash -n` clean, the live unit is **loopback-only / non-root / offline-flagged / no egress**, the smoke batch is **bitwise-stable and exactly matches the sandbox reference** (`calls +2`), every reachable HTTP status path behaves (404 / 400 / 413, 413 refused on the header pre-read), and the non-loopback bind is **refused before model load** (rc 64, no listener). **Two FOLLOW-UPs, neither a blocking-predicate match** (both latent, both coordinator-owned per the brief): **(C-2)** the unit's `ExecStart` points at the **ephemeral lane tree** instead of the contract's main-clone path (AF-AP-122 — the coordinator's repair is to refuse a `.lanes/` path + reinstall from the main clone; it would silently stop on the next lane-tree cleanup), and **(C-1)** the unguarded `int()` on `Content-Length` at `:173` kills a worker thread with no HTTP response on a non-integer value (raw-socket-only edge; the server survives, `/health` stays 200). The 503/500/502 branches are by-design guards (503 unreachable-by-construction from a successful start; 500/502 are the "a model error is a refusal, never a fabricated answer" guards). **No qualifying blocker for the endpoint half.**

---

## Common — D1 (screens on the increment's files + the two builder reports)

- `python3 scripts/report_lint.py --min-refs 12 tasks/briefs/pc-t90-support/T92-report.md --root .` → **`16 refs — OK 16, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`** (SOLID; above the floor, clean).
- `python3 scripts/report_lint.py --min-refs 12 tasks/briefs/jev-laya/PCJ1-report.md --root .` → **`1 refs — OK 1, … MISS 0, …`** + **`FLOOR — OK 1 < --min-refs 12: the report cites too little to be graded`** (SOLID; MISS 0 but the report cites only one `file:NN` ref — a **report-quality FLOOR**, not a false claim; the FLOOR is the gate per the bounded-lint rule, and the builder report under-cites).
- `python3 scripts/ap_screen.py harness-ports/bin/lane-profile.sh harness-ports/bin/pc-lane.sh scripts/pc_lane.sh harness-ports/tests/test_lane_profile.sh` (no `--tests`) → **11 hits over 4 files**: `AF-AP-118 × 10` (every `fallback_providers` occurrence — `lane-profile.sh:46/111/132/137/169×2`, `pc-lane.sh:430`, `test_lane_profile.sh:23/…` — this **IS** the T92 increment's code/tests, so the hits are **new-to-the-increment but by-design**: the registry flags the `fallback_providers` string the whole change exists to manipulate) and `AF-AP-45 × 1` (`pc-lane.sh:122`, the `ps -o pid= --sid …` pids block — **pre-existing**, outside the T92 `:429-444` hunk). **No NEW anti-pattern** is introduced by the T92 diff beyond the `fallback_providers` handling it exists to do.

## FILE IDENTITY

- My lane tree: `HEAD = 433d15e7a32fa365d715f08c55c4e73a7aaa4b27` (the T92 landing; the dispatcher built this tree AT the PIN — `scripts/pc_lane.sh:147-150`; the boundary files are the PIN's — `git diff --quiet 433d15e -- <boundary>` clean; my scratch clone @ 433d15e reproduces every count).
- `scripts/report_lint.py` in this tree is the dispatcher's **current** copy overlaid at launch (not the PIN's) — I never revert it and do not list it in any diff.
- The Hermes CLI source I read for A4(a)/A6: `/home/rocco/.hermes/hermes-agent/hermes_cli/` (the venv's editable install) — `profiles.py` (`delete_profile` → `_canon_valid` → `validate_profile_name`, `_PROFILE_ID_RE` at `:24`) and `config.py` (`:24 import yaml`, `:3324 yaml.safe_load`). These are **outside the repo** (the installed Hermes), read-only, and not part of the boundary — I cite them as the *consumed contract* of the real Hermes, not as files I edited.
