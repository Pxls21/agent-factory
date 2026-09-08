# VERIFY-M1 — adversarial grade of lane M1 (S0-06 four-scope adapter) — PIN `380877b`

**VERDICT: NOT-READY.** One blocking defect: **the PC leg runner cannot complete a run** — the leak
leg queries an ai-memory project that the seeding step never creates, so `collect_leg.sh` aborts
under `set -e` before any bundle is graded (F-1). Everything else is non-blocking hardening, but the
count is large: the checker's substrate "identity" is a format check with nothing to compare against
(F-2/F-3/F-4), the *independent* instrument's own provenance fields are never read (F-5), the
precedence and write assertions never look at content (F-6/F-7), the "no request was made"
instrument is a one-string denylist (F-8), the leak vacuity oracle is a whole-file substring that an
empty recall satisfies (F-9), and **8 hostile bundle shapes crash the checker with a traceback and
no reason line** (F-10), violating the module's own documented exit contract.

**Nothing here mints a hollow green today.** No artifact exists (`proofs/S0-06/result.json` absent,
`proofs/ledger.json` = `{"proof_id":"S0-06","state":"ABSENT"}`), the positive leg defers at exit 2,
and every checker weakness I found turns a *would-be* pass into a pass **only after a real instance
has produced the bundle** — which is exactly when they will matter. The blocking set is F-1 alone;
F-2, F-5, F-8, F-9, F-10 are the set I would fix before the bundle is captured, because re-capturing
on the PC is the expensive step.

**Verdict dependency:** F-1 is proven by static trace + the ai-memory source's own 404 path, **not**
by executing the runner (the brief forbids running it). If the coordinator disagrees with that
trace, the whole NOT-READY rests on it — see F-1's "how to falsify in 30 seconds".

Coordinator note honoured: the lane amended its report on the branch tip (`a449697`) after the PIN —
§8 item 5 and the header row now say the full-`tests/` run was SIGTERMed by its own `timeout 1500`
(exit 143, zero counts) and is replaced by collection evidence (1593 + 95 = 1688), with "the whole
tree EXECUTED" named NOT-done. I graded the PIN's bytes and did **not** file the PIN's older wording
("was still executing") as a discipline finding.

---

## 0. Mechanical gates — pasted

```
report_lint.py tasks/briefs/s0-06-support/M1-report.md --rev 380877b        (no --map)
  report_lint: 84 refs — OK 36, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 48 (at 380877b)   rc=0

report_lint.py … --rev 380877b --map factory_memory.py=proofs/S0-06/adapter/factory_memory.py \
  --map check_four_scope.py=proofs/S0-06/check_four_scope.py \
  --map seed_scopes.py=proofs/S0-06/tools/pc/seed_scopes.py \
  --map run_s0_06_legs.sh=proofs/S0-06/tools/pc/run_s0_06_legs.sh \
  --map start_ai_memory.sh=proofs/S0-06/tools/pc/start_ai_memory.sh \
  --map collect_leg.sh=proofs/S0-06/tools/pc/collect_leg.sh
  MISS   report:274  run_s0_06_legs.sh:24-27  cited line reads:
         '# The identities come from the committed authorization table, never fr'
         tokens ['TMPDIR', 'start_ai_memory.sh', 'S0_06_SRC']
  report_lint: 84 refs — OK 60, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 23 (at 380877b)   rc=1
  (the 23 UNRESOLVED are all ai-memory `crates/…` paths, absent from this repo at any rev — I
   checked those citations by hand against /home/user/nerdherderdani/ai-memory @73715b6f instead)

ap_screen.py proofs/S0-06 proofs/S0-06/adapter proofs/S0-06/tools/pc   (run from the PIN copy)
  --- AP_SCREEN over 3 path(s): 2 hits over 3 files ---
  AP-32: proofs/S0-06/adapter/factory_memory.py:210  hashlib.sha256(...)
  AP-51: proofs/S0-06/check_four_scope.py:21         'byte-identical on a repeat run'
ap_screen.py --tests tests/test_s0_06_four_scope.py
  --- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---
  AF-AP-34: tests/test_s0_06_four_scope.py:995 ×2    AF-AP-35: :826, :833
```
Identical output from the PIN's `.claude/hooks/edit-snapshot.py` and from the shared tree's newer
(uncommitted) one, so the classification is not a stale-screen artifact.

**My classification, by running each hit, not by reading the lane's:**
- **AP-32** — SAFE, agreed and *proven*: `idempotency_path` is the only derivation of the page path,
  and the same call feeds the existence pre-check (`factory_memory.py:352`, `:367`) and the POST
  body (`:373`). I additionally mutated the key (`V9`) and the path (`V8`) — see F-7: the *checker*
  never re-derives it, which is a separate finding, not an AP-32 defect.
- **AP-51** — SAFE, agreed: the `byte-identical` claim is enforced by the `nondet` row
  (`check_four_scope.py:152-154`), killed by the lane's M14 and by my V19.
- **AF-AP-34 ×2** — SAFE, agreed: `tests/test_s0_06_four_scope.py:995` is the test that *bans*
  `pkill`/`killall`/`pgrep`; I confirmed no PC script invokes any of the three.
- **AF-AP-35 ×2** — SAFE, agreed: `:826`/`:833` scrub *honeytokens*, which are synthetic canaries
  committed at `proofs/S0-06/fixtures/honeytokens.json` and quoted verbatim in `spec.json:30`. The
  one real secret (the run-scoped bearer) is asserted absent, never filtered
  (`test_the_token_never_reaches_the_event_stream`, `:546`).

**Report-lint discrepancy (F-17).** The report's §2 pastes
`report_lint: 56 refs — OK 56, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0`. On the PIN's own bytes
the tool finds **84** refs and **1 MISS**. Total-ref count does not depend on `--map`, so the pasted
line was produced against a different (earlier) draft of the report. Minor, but it is the one
mechanical line a verifier is supposed to be able to trust.

---

## 1. Gates I re-ran myself (counts pasted, never typed)

| gate | venue | result |
|---|---|---|
| `pytest tests/test_s0_06_four_scope.py -q --basetemp=…/basetemp/r1 -p no:randomly` on `git archive 380877b` | sandbox | `95 passed in 12.50s`  `PYTEST_RC=0` |
| same, run 2 (`…/basetemp/r2`) | sandbox | `95 passed in 12.61s`  `PYTEST_RC=0` |
| `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_06_four_scope.py` from a clean detached worktree of `380877b`, then `wait` | **PC (the one bridge action)** | `pc_suite: launched 20260908T041342Z-380877b … base 380877bf733fcd6d5f7a36543b1398ed4cadede2 + patch 0B (sha e3b0c44298fc)` → `pytest-exit: 0` / `pytest-summary: 95 passed in 3.07s` |
| `pyflakes` on the 4 Python files | sandbox | rc 0 |
| `bash -n` on the 3 shell scripts | sandbox | rc 0 ×3 |
| `validate-ledger integrity --root .` | sandbox | rc 0; `execution_proof numerator=2 denominator=7` |
| `ledger-gen --root .` then byte-compare to `380877b:proofs/ledger.json` | sandbox | `IDENTICAL` |
| the three spec negative legs + the positive leg | sandbox | see §3 |

**Item 10 — I agree with the checkpoint's PC line.** My PC run carried a **0-byte patch**, i.e. it
executed exactly the PIN's committed bytes, and returned `95 passed in 3.07s` against the
checkpoint's `95 passed in 3.11s`. Same count, both exit 0. No timing claim is made (shared box).

The lane's own `95 ×2` at `773091c` and `4b62a9d` I did **not** reproduce (those revisions are not
the PIN); I reproduced the PIN twice in the sandbox and once on the PC instead.

---

## 2. FINDINGS

### F-1 — BLOCKING. The leak leg queries `agent--a-beta`, which seeding never creates: the PC runner aborts before it grades anything. SOLID.

- `proofs/S0-06/tools/pc/run_s0_06_legs.sh:50-51` seeds with **`--agent "$S0_06_AGENT"`** (default
  `a-alpha`, `:25`).
- `proofs/S0-06/tools/pc/seed_scopes.py:45-51` maps that to the four projects
  `agent--a-alpha`, `project--p-atlas`, `team--t-core`, `_global` — those four, and only those, are
  auto-created by `POST /admin/write-page` (`create_ws_proj`,
  `/home/user/nerdherderdani/ai-memory/crates/ai-memory-mcp/src/admin.rs:6400`).
- `proofs/S0-06/tools/pc/collect_leg.sh:106` and `:115` run the leak leg against
  **`$S0_06_LEAK_AGENT`** (default `a-beta`, `run_s0_06_legs.sh:26`) → the adapter's Agent scope for
  that leg is `agent--a-beta` (`factory_memory.py:107`), and the raw curl is
  `project=agent--a-beta`.
- **`agent--a-beta` does not exist.** `GET /api/v1/search?workspace=factory&project=agent--a-beta`
  resolves through `scoped_search_mode` → `lookup_project`
  (`crates/ai-memory-web/src/routes/api.rs:352-360`, `:993-1007`), which maps
  `ScopeResolutionError::ProjectNotFoundInWorkspace` to **404** `project 'agent--a-beta' not found`
  (`:1002-1004`). `pages_handler` takes the same path (`:161`).

**Expected:** the leak leg captures `leak/recall.json` with `status: ok`, agent+project honeytokens
present, team/company honeytokens absent.
**Observed (traced):** the adapter's `_search` raises `HTTPError` (a `URLError`), caught at
`factory_memory.py:304`, the Agent scope is marked degraded (`:307`), and `recall` returns
`status: "degraded"` with reason `recall: degraded: agent` → CLI exit **3**
(`factory_memory.py:447`). `collect_leg.sh:108-110` runs that command with **no `|| true` and no rc
capture** under `set -euo pipefail` (`:20`) → the leak leg aborts at that line. `run_s0_06_legs.sh:55`
is likewise unguarded, so the whole runner aborts, the EXIT trap stops the instance, and line 61
(`check_four_scope.py "$BUNDLE"`) is **never reached**.
**Second, independent failure on the same wiring:** even if the recall somehow returned `ok`, the
Agent honeytoken `HT-agent-3f1c9a2e` was staged into `agent--a-alpha`, so it is absent from a-beta's
recall and `check_leak` (`check_four_scope.py:213-216`) fails
`leak: authorized honeytoken HT-agent-3f1c9a2e absent from recall` — the lane's own M24 row.
**Failing input:** `bash proofs/S0-06/tools/pc/run_s0_06_legs.sh` with the committed defaults.
**Minimal fix:** seed the leak agent too — after `run_s0_06_legs.sh:51` add

```bash
python3 "$HERE/seed_scopes.py" --base-url "$S0_06_BASE_URL" --token-file "$RUNDIR/token" \
  --agent "$S0_06_LEAK_AGENT" --team "$S0_06_TEAM" --project "$S0_06_PROJECT"
```
(idempotent for the three shared projects; it creates `agent--a-beta` and stages its honeytoken).
**Exact red test** (sandbox-runnable, no ai-memory needed — a pure wiring assertion):

```python
def test_the_leak_legs_agent_scope_is_one_the_runner_seeds():
    runner = (PROOF / "tools" / "pc" / "run_s0_06_legs.sh").read_text()
    seeded = set(re.findall(r'--agent "\$(\w+)"', runner))          # {'S0_06_AGENT', ...}
    leg = (PROOF / "tools" / "pc" / "collect_leg.sh").read_text()
    queried = set(re.findall(r'tuple_file "\$(\w+)"', leg)) | set(
        re.findall(r'project_for "\$scope" "\$(\w+)"', leg))
    assert queried <= seeded, f"leg queries agent scopes never seeded: {queried - seeded}"
```
Run against the PIN it fails with `{'S0_06_LEAK_AGENT'}`; with the fix above it passes.
**How to falsify my trace in 30 s** (coordinator, on the PC, no ai-memory needed):
`grep -n 'ProjectNotFoundInWorkspace' -A3 crates/ai-memory-web/src/routes/api.rs` in the pinned
checkout — if that arm does *not* return `not_found`, F-1's first leg dissolves and only the second
(M24, `leak_empty`) remains, which still blocks.

---

### F-2 — `binary_sha256` is a FORMAT check, not an identity check. SOLID, reproduced.

`check_four_scope.py:138-140` accepts **any** 64-char lowercase-hex string and compares it to
nothing.
**Failing input:** `substrate.json.binary_sha256 = "a"*64`.
**Observed:** `[V1_any64hex] rc=0 :: PASS: S0-06 four-scope - 4/4 assertions, substrate ai-memory
1.39.0@73715b6f`.
**Class:** a format check standing in for an identity check.
**What a real comparison would need — exactly:** *nothing recorded today can serve as the
expected value.* `upstream.lock.yaml:33-38` pins the **source commit**, not a binary digest;
`spikes/rust-ai-memory/result.json` records two `stdout_digest` values for build *logs*, not the
binary; and a release-profile `cargo build` is not bit-reproducible across toolchain/host, so no
constant can be pinned in the repo. The honest options, in order of cost:
1. **Bind the digest to the run that produced it** — `start_ai_memory.sh:67` already computes
   `BIN_SHA`; have it *also* record `bin_path`, `cargo --version` and `rustc --version` into
   `substrate.json`, and have the checker require the digest to match a *second* independent read
   of the same binary recorded by `collect_leg.sh`. That upgrades "any hex" to "the same binary
   throughout the run", which is what the field is actually able to claim.
2. **Delete the field's pretence**: rename it `binary_sha256_observed` and say in the docstring that
   it is provenance, not identity, so no future reader mistakes it for a pin.
3. Record a first digest on the first PC run and pin it in `upstream.lock.yaml` as
   `observed_binary_sha256_pc` — only honest if the same toolchain is used every time.
**Minimal fix now:** (2) plus a comment naming (1) as the follow-up.
**Exact red test:** `assert run(bundle_with(binary_sha256="a"*64)) == (1, REASONS["substrate_pin"]…)`
— red today.

---

### F-3 — the version half of the substrate pin is a checker literal while `upstream.lock.yaml` carries it. SOLID, reproduced.

`check_four_scope.py:39` `EXPECTED_VERSION = "1.39.0"`, while `upstream.lock.yaml:36` carries
`observed_version: 1.39.0` and the pinned `Cargo.toml:20` carries `version = "1.39.0"`.
`test_the_pinned_commit_comes_from_upstream_lock_not_the_checker`
(`tests/test_s0_06_four_scope.py:953`) protects the **commit** only.
**Failing input:** edit the lock to `observed_version: 1.40.0`.
**Observed:** `observed_version bumped to 1.40.0  rc=0 out='PASS: … 1.39.0@73715b6f'` — the checker
happily grades a bundle against a version the lock no longer pins.
**Minimal fix:** `EXPECTED_VERSION` comes from `_pinned_version()` reading
`lock["selected_core"]["ai-memory"]["observed_version"]`, exactly as `_pinned_commit` does at `:121`.
**Exact red test:** extend `:953` to assert the checker source contains no `"1.39.0"` literal.

---

### F-4 — `substrate.json` records the producer's own constants and its INTENT, never a readback. SOLID (static, cross-checked against the producer).

`start_ai_memory.sh:118-135` writes `commit` and `version` from its **own** literals
(`PINNED_COMMIT` `:23`, `PINNED_VERSION` `:24`) and writes the `posture` block as a **hardcoded
echo** of the four `export`s at `:82-85`. So `check_substrate`'s commit/version/posture assertions
compare the checker's constants to the script's constants. The one field that *is* an observation —
`version_stdout` (`:133`, from `"$BIN" --version`, `:112`) — the checker never reads.
Two consequences:
- **config-presence ≠ delivery.** Nothing verifies the instance *accepted* the four `AI_MEMORY_…`
  variables. If the `__` nesting ever changes (`config.rs:937`) or a key is renamed upstream, the
  posture silently does not apply and `substrate.json` still says it did. `require_approval`
  defaults **false** (`crates/ai-memory-cli/src/config.rs:702`, `:812`), so this is the exact
  variable whose delivery matters.
- The committed fixture bundles carry **no `version_stdout` key at all**
  (`proofs/S0-06/fixtures/evidence-*/substrate.json`), i.e. they could not have been produced by
  `start_ai_memory.sh` — a producer/fixture drift the key-set tests do not cover (they cover
  `ApiSearchHit`/`PageSummary` only, `tests/…:602`).
**Minimal fix, two lines:** in `check_substrate`, `if EXPECTED_VERSION not in doc.get("version_stdout",""): raise Fail("substrate_pin", got=f"version_stdout={...}")`;
and in `start_ai_memory.sh` capture the posture by **reading it back** — `ai-memory` has no config
dump endpoint I could find, so the honest minimum is to record `env | grep ^AI_MEMORY_` of the
*child's* environment (`/proc/$SERVE_PID/environ`, tr '\0' '\n') rather than re-typing the exports.
**Exact red test:** a bundle whose `posture` block says `true` while `/proc/<pid>/environ` says
`false` must fail — today it passes, because no environ is captured.

---

### F-5 — the "independent instrument" never has its own provenance checked. SOLID, reproduced ×2.

`ApiSearchHit` carries `workspace` and `project`
(`crates/ai-memory-web/src/routes/api.rs:1254-1263`, re-derived by `sed -n '1250,1268p'`), and the
fixtures carry them. `check_precedence` (`check_four_scope.py:158-168`) and `check_leak`
(`:206-216`) read only `path`, `title` and raw text — never `project`/`workspace`.
**Failing inputs / observed:**
- `precedence/raw-team.json` entries rewritten to `"project": "agent--a-alpha"` →
  `[V4_raw_team_wrong_project] rc=0 :: PASS`
- all four precedence raw reads rewritten to `"workspace": "somewhere-else"` →
  `[V5_raw_wrong_workspace] rc=0 :: PASS`
So four copies of the **same** project's search response satisfy the "four distinct scopes" instrument
as long as the titles differ. The second instrument's independence is asserted by the *collection
script*, never by the checker.
**Minimal fix** (in `check_precedence` and `check_leak`, ~4 lines):
```python
EXPECTED_PROJECT = {"agent": None, "project": None, "team": None, "company": "_global"}  # agent/…
for s in SCOPE_ORDER:
    for e in raw[s]:
        if e["workspace"] != "factory" or not _project_matches(s, e["project"]):
            raise Fail("raw_provenance", scope=s, project=e["project"])
```
with the agent/project/team names taken from `precedence/tuple.json` (which `collect_leg.sh:72`
already writes into the bundle and the checker currently ignores).
**Exact red test:** V4 above, asserted to exit 1 with the new `raw_provenance` reason.
**Note the real limit:** `PageSummary` has **no** project field (`reader.rs:1174-1185`), so the
`write-scope/raw-*.json` files genuinely cannot be provenance-checked from their payload. Fixing
that needs `collect_leg.sh` to record the URL it fetched alongside each raw file. Say so rather than
pretending both legs can be closed the same way.

---

### F-6 — the precedence winner's CONTENT is never compared to the agent scope's record. SOLID, reproduced.

`check_four_scope.py:169-175` asserts only `merged[0]["scope"] == "agent"` and the shadowed list.
**Failing input:** rewrite the merged winner's `provenance.title` and `provenance.snippet` to the
**team** variant, keeping `scope: "agent"`.
**Observed:** `[V6_winner_carries_team_content] rc=0 :: PASS`.
So the assertion "the Agent copy wins" is proven at the level of a label, not of the bytes the caller
would receive — which is the whole point of staging four different bodies
(`records-precedence.json:4-21`).
**Minimal fix (3 lines):**
```python
agent_hit = next(e for e in raw["agent"] if e["path"] == sid)
prov = merged[0]["provenance"]
if prov.get("title") != agent_hit["title"] or prov.get("snippet") != agent_hit["snippet"]:
    raise Fail("winner_content", sid=sid, got=prov.get("title"))
```
**Exact red test:** V6, asserted to exit 1.

---

### F-7 — the write assertion is path-only: neither the record's content nor the derivation of the path is checked. SOLID, reproduced ×3.

`check_four_scope.py:184-193` compares `write["page_path"]` to `e["path"]` in the raw listings and
nothing else. `PageSummary` carries `title`, `kind`, `tier` (`reader.rs:1174-1185`); the record
written by `collect_leg.sh:85-92` has a known body and the adapter sends `kind: "fact"`,
`tier: "semantic"` (`factory_memory.py:376-377`).
**Failing inputs / observed:**
- raw-agent entry's `title`/`kind`/`tier` changed to unrelated values → `[V7_write_content_mismatch] rc=0 :: PASS`
- `write.json`/`retry.json`/`raw-agent` all moved to `observations/deadbeefdeadbeef.md`, a path **not**
  derivable from the idempotency key → `[V8_page_path_not_derived] rc=0 :: PASS`
- `idempotency_key` replaced with `{"session":"X","turn":"Y","event_id":"Z"}` → `[V9_idem_key_mutated] rc=0 :: PASS`
V8 is the sharpest: `idempotency_path` (`factory_memory.py:201-210`) is the mechanism the proof
claims — "retries are idempotent by session/turn/event ID" (docs/03 §4 write contract) — and the
checker never re-derives it.
**Minimal fix (4 lines), and it needs no new evidence:**
```python
import hashlib
key = write["idempotency_key"]
want = "observations/" + hashlib.sha256("\x1f".join(
    [key["session"], key["turn"], key["event_id"]]).encode()).hexdigest()[:16] + ".md"
if page_path != want: raise Fail("write_path_not_derived", got=page_path, want=want)
if found[0].get("kind") != "fact" or found[0].get("tier") != "semantic":
    raise Fail("write_content", got=found[0])
```
(re-deriving in the checker duplicates 3 lines of the adapter — that is *deliberate*: an oracle that
imports the subject is a mirror, `anti-hollow-green` §4.)
**Exact red test:** V8, asserted to exit 1.

---

### F-8 — the "no request was made" instrument is a denylist of one exact string. SOLID, reproduced ×3.

`check_four_scope.py:235` `if any(e["event"] == "http_request" for e in events)`.
**Failing inputs / observed** (each keeps the required `scope_tuple_denied` event):
- append `{"event":"http-request", …}` → `[V13_denied_http_hyphen] rc=0 :: PASS`
- append `{"event":"HTTP_REQUEST", …}` → `[V15_denied_uppercase] rc=0 :: PASS`
- append `{"event":{"event":"http_request"}}` → `[V14_denied_nested_event] rc=0 :: PASS`
  (`"event" in event` is true, so the `denied_stream` guard at `:232-233` does not fire, and
  `dict == str` is false).
The *empty*-stream case is safe: `[V16_denied_empty_stream] rc=1 :: denied: leg did not record the
tuple denial` (the lane's M26 row), so "zero events" cannot pass trivially — good.
**Minimal fix — make it an allowlist, one line:**
```python
seen = {e["event"] for e in events}
if seen != {"scope_tuple_denied"}: raise Fail("denied_request", got=sorted(seen))
```
The denied leg's stream is a *closed* set by construction (I reproduced it: exactly one event, see
§3), so an allowlist costs nothing and closes all three variants plus every future event name.
**Exact red test:** V13/V14/V15, each asserted to exit 1.

---

### F-9 — the leak vacuity oracle is a whole-file substring, so an EMPTY recall passes. SOLID, reproduced ×2.

`check_four_scope.py:213-216` tests `token not in recall_text`, where `recall_text` is the **whole
file** (`:204`). The forbidden half (`:207-212`) is also whole-file, which is correctly conservative
(my `[V12_forbidden_token_in_debug_field] rc=1 :: leak: honeytoken HT-team-c52e6f04 surfaced from
team` — a token hidden in a stray key still fires). The *authorized* half is the problem: it is the
oracle's own anti-vacuity self-test (the report's M24 rationale), and it is satisfiable with
`records: []`.
**Failing inputs / observed:**
- `records: []` plus `"note": "queried for HT-agent-… and HT-project-…"` → `[V10_empty_recall_token_in_stray_field] rc=0 :: PASS`
- `records: []` plus `scopes_queried` rewritten to carry the token strings → `[V11_empty_recall_token_in_scopes_queried] rc=0 :: PASS`
**Minimal fix (2 lines):** scope the authorized half to the records —
```python
records_text = json.dumps(json.loads(recall_text)["records"], sort_keys=True)
for scope in LEAK_AUTHORIZED:
    if tokens[scope] not in records_text: raise Fail("leak_empty", token=tokens[scope])
```
Keep the forbidden half on the whole text (conservative is correct there).
**Exact red test:** V10, asserted to exit 1 with `leak_empty`.
**Related, non-blocking:** `LEAK_AUTHORIZED`/`LEAK_FORBIDDEN` (`:43-44`) are constants, not derived
from `leak/tuple.json` — which `collect_leg.sh:106` writes into the bundle and the checker never
reads. The checker therefore cannot confirm the leak recall came from the agent+project-only
binding. It fails safe (a fully-authorized binding would surface team/company tokens and trip
`leak`), so this is an observation, not a hole.

---

### F-10 — 8 hostile bundle SHAPES crash the checker with a traceback and no reason line. SOLID, reproduced ×8.

The module's own contract (`check_four_scope.py:7-8`): *"Exit 0 + the PASS line · exit 1 + ONE exact
reason from REASONS · exit 2 + `deferred: …`"*. The lane's 28 mutants all perturb field **values**;
none perturbs a **shape**. Every one of these exits 1 with an empty stdout and a Python traceback:

| input | crash |
|---|---|
| `leak/honeytokens.json` missing the `team` key | `KeyError: 'team'` (`:208`) |
| a `precedence/raw-*.json` entry missing `path` | `KeyError: 'path'` (`:161`) |
| a `raw-*.json` that is a JSON **object** | `TypeError: string indices must be integers` (`:161`) |
| `recall.records` is an object | `TypeError: string indices…` (`:169`) |
| `write-scope/write.json` without `page_path` | `KeyError: 'page_path'` (`:184`) |
| `substrate.json` is a JSON array | `AttributeError: 'list' object has no attribute 'get'` (`:133`) |
| `substrate.posture` is a string | `AttributeError: 'str' object has no attribute 'get'` (`:143`) |
| a merged record without `scope` | `KeyError: 'scope'` (`:171`) |
| **and** an absent `proofs/S0-06/adapter/bindings.json` | `FileNotFoundError` (`factory_memory.py:117`) |

`[H8_events_is_array] rc=1 :: denied: event stream unreadable` and `[H9_leak_no_status] rc=1 ::
leg: leak/recall.json status None, expected ok` show the two shapes that *are* handled.
**Why it matters even though nothing mints:** AF-AP-36 says a checker is graded against hostile
bundles, never only its own golden; and a proof whose failure mode is a traceback gives the operator
no reason string to paste, which is precisely the discipline `spec.json`'s `failure_reason` exists
to enforce.
**Minimal fix (5 lines, one place):** wrap the four `check_*` bodies —
```python
def run(root):
    ...
    for name, fn in (("denied", check_denied), ("precedence", check_precedence),
                     ("write-scope", check_write_scope), ("leak", check_leak)):
        try: fn(root)
        except (KeyError, TypeError, AttributeError, IndexError) as exc:
            raise Fail("shape", leg=name, detail=f"{type(exc).__name__}: {exc}")
```
plus `"shape": "leg: {leg} evidence shape invalid ({detail})"` in `REASONS`, and the same wrapper
around `check_substrate`.
**Exact red test:** parametrise the eight bundles above and assert
`rc == 1 and out.startswith("leg: ") and "Traceback" not in stderr`.

---

### F-11 — `recall()` crashes instead of degrading on any malformed 200 response: `normalize_hit` sits OUTSIDE the try, and `TypeError` is not caught. SOLID, reproduced ×4 against a loopback server.

`factory_memory.py:301-311`: the `try` covers `_search` and `_page_times`; the list comprehension
that calls `normalize_hit` is at `:311`, **after** the `except`. The comment at `:305-306` ("Any
scope authorization ambiguity or read outage fails closed FOR THAT SCOPE and is named in the status
(docs/04 §4); never a silent partial") therefore over-claims: it covers transport and
`_page_times`'s own `KeyError`, not the search-hit shape.
**Failing inputs / observed** (recording server on 127.0.0.1, started and closed in-process):

| body returned by `/api/v1/search` | observed |
|---|---|
| a hit without `rank` | `UNCAUGHT KeyError: 'rank'` |
| a hit without `path` | `UNCAUGHT KeyError: 'path'` |
| `{"hits": []}` (object, not array) | `UNCAUGHT TypeError: string indices must be integers, not 'str'` |
| `["oops"]` | `UNCAUGHT TypeError: …` |
| `null` | `UNCAUGHT TypeError: 'NoneType' object is not iterable` |

Under the CLI this means: no `--out` file, no reason line, and **exit 1 — the same code as
`denied`** (`factory_memory.py:447` maps only ok/denied/degraded). A spec leg pinning
`denied: scope-tuple-unauthorized` on exit 1 cannot distinguish a denial from a crash.
**Minimal fix (2 lines):** move `:311` inside the `try`, and add `TypeError` to the tuple at `:304`
(and at `:363`, `:382`).
**Exact red test:**
```python
def test_a_malformed_search_hit_degrades_the_scope_instead_of_crashing(server):
    server.next_search = [{"path": "notes/x.md"}]          # no rank
    r = fm.FactoryMemory(base_url=server.base_url).recall(AUTHORIZED_TUPLE, "q")
    assert r["status"] == "degraded" and r["degraded_scopes"] == ["agent", "company", "project", "team"]
```
red today (raises `KeyError`).

---

### F-12 — `_pinned_commit` has no failure path, and PyYAML silently accepts a duplicate `ai-memory:` key. SOLID, reproduced ×3.

`check_four_scope.py:121-125`. I rebuilt a minimal repo skeleton and mutated only the lock:

| lock mutation | observed |
|---|---|
| `selected_core:` renamed | `rc=1 out='<none>' err="KeyError: 'selected_core'"` |
| `commit:` renamed to `sha:` | `rc=1 out='<none>' err="KeyError: 'commit'"` |
| a **second** `ai-memory:` block appended under `selected_core` | parsed, **last one wins** (`rc=1`, the reason names the *first* block's commit only because the bundle carries it) |

**Minimal fix:** `try: … except (KeyError, TypeError): raise Fail("substrate_pin", got="upstream.lock.yaml has no selected_core.ai-memory.commit")`, and — for the duplicate — load with a
`yaml.SafeLoader` subclass whose `construct_mapping` refuses duplicate keys (8 lines), or simply
assert `text.count("\n  ai-memory:") == 1` before parsing (1 line).
**Also:** `import yaml` is *inside* the function (`:122`), so an environment without PyYAML gives a
traceback rather than a named reason; the report's class-10 row claims module-scope imports matching
CI's declared deps, which is true of the **test** module, not of the checker.
**Exact red test:** the renamed-key lock, asserted to exit 1 with a `REASONS` value.

---

### F-13 — `merge` can list the winner's OWN scope in `shadowed_scopes`, with duplicates. SOLID, reproduced.

`factory_memory.py:180-183`: two records with the same `stable_id` inside **one** scope make the
second append that same scope to `shadowed`.
**Observed:** `merge({"agent":[recA, recB]})` → 1 winner, `provenance.shadowed_scopes == ['agent']`;
three copies → `['agent', 'agent']` (not de-duplicated either).
`check_precedence` (`:172-175`) only requires the other three scopes to be *present*, so a
self-shadow passes.
**Reachability, honestly:** `(workspace, project, path)` is unique in ai-memory, and
`search_scopes` de-duplicates by page id
(`crates/ai-memory-web/src/routes/api.rs:404-414`), so a real single-scope search should not return
one path twice — this is a domain hole, not an observed live bug. It matters because `merge` is a
pure function the proof advertises as deterministic over its whole input domain.
**Minimal fix (1 line):** `shadowed.setdefault(sid, set()).add(scope)` and drop `scope == winner
scope`, i.e. `sorted(shadowed.get(sid, set()) - {winner["scope"]}, key=SCOPE_ORDER.index)`.
**Exact red test:** `assert merge({"agent":[r,r]})[0]["provenance"]["shadowed_scopes"] == []`.

---

### F-14 — an unrecognised scope name in a bindings row is silently dropped. SOLID, reproduced.

`factory_memory.py:254` intersects the row's `scopes` with `SCOPE_ORDER`; a typo (`"porject"`) or an
invented scope (`"admin"`) simply vanishes. Fail-**closed** (access narrows), and the narrowing *is*
visible in `scope_tuple_authorized.authorized_scopes`, so this is low severity — but a typo in the
committed authorization table produces a quietly weaker binding with no refusal.
**Observed:** row `scopes: ["agent","porject","admin"]` → event
`{"authorized_scopes": ["agent"], "event": "scope_tuple_authorized", …}`, recall queries one scope.
`merge` drops out-of-order scopes the same way (`merge({"admin": [...], "agent": [...]})` returns the
agent record only).
**Minimal fix (2 lines) in `load_bindings`:** `if set(row.get("scopes", [])) - set(SCOPE_ORDER):
raise ValueError(f"bindings row {row['agent']} names unknown scopes …")` — a committed-table typo
should be a hard load failure, not a silent narrowing.
**Exact red test:** `pytest.raises(ValueError)` on a table with `"porject"`.

---

### F-15 — the adapter emits non-RFC-8259 JSON for a non-finite `rank`. SOLID, reproduced.

`factory_memory.py:185` (`json.loads(json.dumps(...))`) and `:443` (`--out`) use default
`allow_nan=True`.
**Observed:** `rank=nan → bytes-identical=True, confidence emitted as nan, strict-json=REJECTED(NaN)`;
same for `inf`. So the `nondet` row is *not* wormholed (both runs emit the same bytes), but the
bundle stops being JSON any strict parser will read (`jq`, `serde_json`, `json.loads(...,
parse_constant=…)`), and the checker's own `json.loads` accepts it silently.
**Reachability, honestly:** `rank` is `f64` (`api.rs:1262`) and `serde_json` serialises a non-finite
f64 as `null`, so a real substrate sends `null`, not `NaN` — this is a hardening item, not a live
path.
**Minimal fix (1 line each):** `json.dumps(..., allow_nan=False)` at `:185` and `:443`; a
non-finite confidence then raises `ValueError`, which `:304` already catches → the scope degrades
with a named reason.
**Exact red test:** feed the recording server `"rank": 1e999`-equivalent (`float("inf")` via a raw
body) and assert `status == "degraded"`.

---

### F-16 — the PC runner's enumerated external-command list is wrong in both directions. SOLID, reproduced.

`run_s0_06_legs.sh:14-15`, `start_ai_memory.sh:13-14`, report §1.4 all enumerate
`bash, git, cargo, curl, python3, ss, sha256sum, install, mkdir, mktemp, kill, readlink, cp, sed,
awk, cat, chmod, seq, sleep, date, tr, cut`.
- **Invoked but not listed:** `grep` (`start_ai_memory.sh:32`), `nohup` (`:91`), `head` (`:112`).
- **Listed but never invoked:** `date`, `chmod` (0 occurrences in any of the three scripts).
The brief calls a missed command a finding; three are missed. It matters because that list is the
sandbox-vs-PC portability contract for a script that will run on the owner's box.
**Minimal fix:** correct both header comments and the report's §1.4 line.
**Exact red test:** the existing `test_pc_runner_*` family gains
```python
def test_the_enumerated_external_commands_match_the_scripts():
    declared = set(re.search(r"External commands used: (.+?)\.\n", text, re.S).group(1).replace("\n#","").split(", "))
    used = set(re.findall(r"(?m)^\s*(?:nohup\s+)?([a-z0-9_]+)\s", stripped_of_comments))
    assert used - declared == set() and declared - used == set()
```

---

### F-17 — the report's pasted `report_lint` line does not reproduce, and one MISS exists. SOLID, reproduced. (See §0.)

`tasks/briefs/s0-06-support/M1-report.md:160` claims `56 refs — OK 56 … UNRESOLVED 0`; the PIN's
bytes give `84 refs … MISS 1 … UNRESOLVED 23`. The MISS is at report line 274, the class-6 row, whose single citation is wrong twice.
The four scope-id exports are `run_s0_06_legs.sh:25-28` (the cited range starts on the comment and
stops one line short of `S0_06_PROJECT`).
The `TMPDIR` domain is `run_s0_06_legs.sh:30`, a different line entirely.
**Minimal fix:** re-run the linter on the final bytes, re-paste the summary, and split that class-6
citation in two.

---

### F-18 — the run-scoped bearer token is derived two different ways, and the run dir keeps it. SOLID (static) / partly UNSURE.

`start_ai_memory.sh:75` builds `curl.cfg` from the token file's **last line**
(`sed -e '$!d'`); `:87` builds `AI_MEMORY_AUTH_TOKEN` from **`$(cat …)`** (the whole file). They
agree only if `generate-auth-token` prints exactly one line. I verified the pinned source does
(`crates/ai-memory-cli/src/commands/generate_auth_token.rs:26` `println!("{token}")`), so this is
benign **today** — but nothing asserts it, and a future banner line silently splits the two
derivations (curl authenticates, the server expects something else → the readiness wait exits 69).
- **Token hygiene is otherwise sound and I checked it by hand:** no `set -x` anywhere; the token
  never appears in argv (`--config`, AF-AP-39) and never in an `echo`/`printf` of its value; both
  `token` and `curl.cfg` are created `install -m 0600`; `factory_memory._emit` (`:232-244`)
  serialises only named fields and the token is not among them — I confirmed empirically that the
  event stream of a real run carries no token.
- **The kept run dir (`run_s0_06_legs.sh:62`, report §10).** My judgement: **acceptable, but change
  the default.** `mktemp -d` gives 0700 and the two secret files are 0600, so the exposure is to
  root and to the owner's own account only, and the token dies with the instance (it authenticates
  nothing after the process exits — a fresh one is generated per run). What is *not* acceptable is
  leaving it with no expiry on a long-lived box: the honest minimum is `shred -u
  "$RUNDIR/token" "$RUNDIR/curl.cfg"` in `stop_instance` (after the last curl), keeping
  `serve.log` + `substrate.json`, and printing the path so the operator can inspect the log. That
  costs one line and loses nothing the operator needs.
**Exact red test:** `assert "shred" in run_s0_06_legs.sh` plus a unit that runs `stop_instance` in a
fake run dir and asserts `token`/`curl.cfg` are gone and `serve.log` remains.

---

### F-19 — `$S0_06_SRC` defaults into `$HOME` and force-detaches a checkout it did not create. SOLID (static).

`start_ai_memory.sh:25` `SRC="${S0_06_SRC:-$HOME/s0-06-pinned/ai-memory}"`, then `:55-56`
`git -C "$SRC" fetch … && git -C "$SRC" checkout --quiet --detach "$PINNED_COMMIT"`. If a clone
already exists at that path (the lane's own working clone is at
`/home/user/nerdherderdani/ai-memory`, but the PC path is a plausible collision with the S0-01
`~/s0-01-pinned` convention), the script silently moves it to a detached HEAD.
It is *guarded* by `:57-58` (`HEAD_SHA` must equal the pin, else exit 66) so it cannot build the
wrong bytes — the risk is to a human's working tree, not to the proof.
**Minimal fix:** clone into `"$RUNDIR/src"` when `S0_06_SRC` is unset, or refuse when
`git -C "$SRC" status --porcelain` is non-empty.
**`HOME` is also a 6th class-6 env domain** the report's row (3, at `:274`) does not count.

---

### F-20 — no test proves the `bindings.json` S_ISREG guard is load-bearing. SOLID, reproduced by mutation.

Mutation audit (§4): deleting the guard at `factory_memory.py:117-118` leaves the suite at
**`95 passed`** — the only one of my ten injected bugs that survives.
The guard itself is correct (I verified: directory → `ValueError`, FIFO → `ValueError`, **symlink to
the real table → `ValueError`** because `lstat` is used, plain copy → 3 rows loaded).
**Minimal fix:** one parametrised test over `{dir, fifo, symlink}` asserting `pytest.raises(ValueError)`.

---

### F-21 — read paths are S_ISREG-guarded, write paths are not. SOLID (static).

Every read in the lane's code lstat-guards (`factory_memory.py:117`, `:393`, `:403`;
`check_four_scope.py:96-100`; `seed_scopes.py:40`, `:86`). The two writes —
`Path(args.out).write_text(...)` (`factory_memory.py:443`) and `open(args.events, "w")` (`:430`) —
follow symlinks. The report calls class 17 (hardlink-clobbering writes) an **empty class**; it is a
*documented limit* instead, since the paths are runner-chosen. Low severity, but the asymmetry is
worth one line of comment or `O_NOFOLLOW|O_CREAT|O_EXCL`.

---

### F-22 — an evidence root that is a symlink is accepted. SOLID, reproduced.

`check_four_scope.py:242` `root.is_dir()` follows symlinks; `_read_text` lstats the files *inside*
the target. A symlinked bundle root grades identically:
`(H11) rc=0 out='PASS: S0-06 four-scope - 4/4 assertions…'`. The runner creates the bundle itself, so
this is a consistency note (the module's docstring makes a point of lstat discipline), not a hole.
**Minimal fix:** `if root.is_symlink() or not root.is_dir(): raise Deferred()/Fail(...)`.

---

### F-23 — the fixtures' `snippet` values carry no `<mark>` decoration that real snippets carry. SOLID (source-verified).

Real snippets come from `snippet(pages_fts, 1, '<mark>', '</mark>', '…', 24)`
(`crates/ai-memory-store/src/reader.rs:1483`, `:1565`, `:1689`); the committed fixtures use plain
prose (`evidence-leak/leak/raw-team.json`, `evidence-leak/precedence/raw-agent.json`). The
`PROVENANCE.md` files honestly declare every snippet SYNTHETIC, and the checker's substring tests are
unaffected (the honeytoken is not the query term, so no marks land inside it). Recording it because
the report's self-attack B names field **semantics** as the residual risk and this is a concrete
instance of it. The related *window* worry the brief raises is **not** a risk: the canary body
(`records-precedence.json:30`) is ~12 tokens against a 24-token window, so the token is always
inside the snippet.

---

### F-24 — a latent `nondet` false red on a fuller corpus. UNSURE (source-reasoned, not observed).

`search_scopes` collects a `HashMap` into a `Vec`, sorts with
`a.rank.partial_cmp(&b.rank).unwrap_or(Ordering::Equal)` and then `truncate(limit)`
(`api.rs:416-423`). Rust's `HashMap` iteration order is randomised per instance and `sort_by` is
stable, so **rank ties keep a randomised order**; with more than `limit` (20) tied hits, *which*
survive `truncate` can differ between the two recalls, changing the record **set** and tripping
`merge: nondeterministic`. The adapter's `merge` normalises **order** (sorted by `(rank, sid)`), so
ordering alone is safe — it is the truncation boundary that is not. The seeded corpus is 3 pages per
scope, so this cannot fire on the runner as written; it can fire if the fixture ever grows or if the
proof is ever pointed at a populated instance.
**Minimal fix (in the proof, not upstream):** keep `--limit` comfortably above the seeded corpus
(already true) and add a one-line note in `check_four_scope.py`'s `nondet` docstring naming this as
the one non-adapter cause of that row, so a future red is diagnosed in seconds rather than blamed on
`merge`.

**On D-4 specifically** (the brief asks whether `recall-1`/`recall-2` can differ in `updated_at`
without a write): **no, not on this runner.** `updated_at` is
`jiff::Timestamp::from_microsecond(updated_us).to_string()` (`reader.rs:6022-6030`), a pure function
of the stored column, and `run_s0_06_legs.sh:54` runs the legs in the order
`denied precedence write-scope leak` — the only write happens **after** both precedence recalls.
The consistency window D-4 worries about is real in principle (two GETs per scope) but is not
reachable in this leg order. If the order ever changes, the fix is to compare the record **minus**
`timestamp`, not to take the listing once.

---

### F-25 — the recall query text is written into the event stream. SOLID, reproduced. (Low.)

`factory_memory.py:269` emits `path=` for every request, and `_search` (`:275-278`) puts the
caller's `--query` into that path (`"/api/v1/search?q=q&workspace=factory&project=agent--a-alpha&limit=20"`
in my run). In this proof the queries are `deploy window`/`honeytoken`; in production a recall query
is model- or user-derived text landing in a decision log. Worth one line of comment or emitting
`path` without the query string.

---

### F-26 — item 9, the 18-class re-scan: the classes I re-derived, and the one answer the brief asked for.

I re-scanned the 12 code/test files. I agree with 16 of the lane's 18 rows, including the four it
declares **empty** (7 lossy decodes, 10 skips/xfails, 15 two-counter mismatches, 17 —
see F-21 for why 17 is a documented limit rather than empty). Two rows I would change:
- **class 6 (env-domain fail-opens)** — 3 declared, I count **6**: the four scope ids as *four*
  (they feed two different consumers — the seeder and the tuple builder), plus `TMPDIR`, plus
  `HOME` (F-19). **The brief's worry does not hold, and this is the useful result:** a typo'd
  `S0_06_TEAM`/`S0_06_PROJECT`/`S0_06_AGENT`/`S0_06_LEAK_AGENT` cannot green anything, because
  `collect_leg.sh:59-68` builds the tuple **from those same variables** and the adapter matches it
  verbatim against the committed table — a typo produces
  `denied: scope-tuple-unauthorized`, exit 1, and `set -e` aborts the leg. The table is the
  fail-closed backstop for the whole class. (What a typo *does* leave behind is junk projects in the
  run's throwaway data dir — harmless.) `S0_06_TOOLCHAIN` fails the cargo build loudly;
  `S0_06_SRC`/`HOME` are F-19.
- **class 3 (`[-1]` reads)** — closed in the tests, agreed; but the *checker* now has 8 shapes that
  print **nothing** to stdout (F-10), so a consumer doing `stdout.splitlines()[-1]` gets an
  `IndexError` instead of a reason. The class is closed at the assertion site and re-opened at the
  producer.

---

## 3. Negative controls (item 6) — all reproduced exactly on the PIN

```
$ python3 proofs/S0-06/adapter/factory_memory.py recall \
      --tuple-file fixtures/s0-06/neg-unauthorized-tuple.json --query x
denied: scope-tuple-unauthorized                                  rc=1
$ python3 proofs/S0-06/check_four_scope.py proofs/S0-06/fixtures/evidence-leak
leak: honeytoken HT-team-c52e6f04 surfaced from team               rc=1
$ python3 proofs/S0-06/check_four_scope.py proofs/S0-06/fixtures/evidence-wrong-scope-write
write: record found in project                                     rc=1
$ python3 proofs/S0-06/check_four_scope.py proofs/S0-06/evidence
deferred: S0-06 evidence not captured                              rc=2
```
All three match `spec.json:20,30,40` byte-for-byte, and the positive leg defers → `scripts/proof-runner`
raises `Deferred` at `:181-182` and mints nothing. The seed's literal path
`fixtures/s0-06/neg-unauthorized-tuple.json` matches `seeds/seed-stage0-v1.yaml:457`.

**The one wrong field is `team`.** The fixture is
`{actor: svc-agent-runner, agent: a-alpha, team: t-platform, project: p-atlas}`; the a-gamma row
(`bindings.json:19-25`) binds `t-platform` together with `a-gamma` and `p-borealis`, while
`a-alpha`'s row (`bindings.json:5-11`) binds `t-core`. So `t-platform` is a real team, borrowed from another row — a real-looking tuple, as
claimed. Confirmed by running `authorize` over the whole corruption domain (§4).

**"No network call" — proven with a paired positive control, not by absence.** I started a loopback
listener that **accepts and never answers**, and counted accepts:

```
hang-server port=37219 (accepts, never responds)
  negative fixture : rc=1 stdout='denied: scope-tuple-unauthorized'  elapsed=0.07s  accepted_connections=0
  POSITIVE CONTROL (authorized a-beta tuple, same port, --timeout-s 2):
                     rc=3 stdout='recall: degraded: agent,project'   elapsed=4.07s  accepted_connections=2
```
The instrument fired (2 accepts for the control, 0 for the denial), so the zero is evidence, not
silence. Against a **closed** port the denial is identical and the event stream contains exactly one
line: `{"event": "scope_tuple_denied", "presented_fields": ["actor","agent","project","team"],
"reason": "denied: scope-tuple-unauthorized", "seq": 1}`.

---

## 4. Mutants — 28 (lane, spot-reproduced) + 31 of mine = 59

**Lane mutants reproduced.** I did not re-run all 28; I reproduced the whole class by mutating the
checker itself (below), and I reproduced these specific rows through my own driver: M01 `deferred`,
M21 `write: idempotent retry produced 2 records` (my V20), M24-class `leak_empty` (my V19 for
`winner`), M26 `denied: leg did not record the tuple denial` (my V16), the two committed-bundle
negatives (§3). The lane's killer lines I checked matched verbatim.

**Red control reproduced (report §5 defect 2).** Reverting the `authorize` guard on a scratch copy
(`factory_memory.py:139-141` → the pre-fix `tuple_obj[f] == row.get(f)`) turns the suite red at
exactly the claimed test:
```
FAILED tests/test_s0_06_four_scope.py::test_a_malformed_table_row_can_never_authorize_a_null_tuple
E  AssertionError: assert {'actor': 'svc-agent-runner', 'agent': 'a-alpha', 'team': 't-core'} is None
```
— the same line the report pastes. The test was genuinely red before the fix.

**Mutation audit of the gate itself** (10 injected bugs, each on its own scratch copy, suite re-run):

| injected bug | suite |
|---|---|
| C1 `check_leak` leak check tautologied | 3 failed, 92 passed |
| C2 `check_denied` http_request check removed | 1 failed, 94 passed |
| C3 posture loop emptied | 2 failed, 93 passed |
| C4 `nondet` byte compare tautologied | 1 failed, 94 passed |
| C5 `write_found` loop emptied | 2 failed, 93 passed |
| C6 `authorize` reverted to `row.get` | 1 failed, 94 passed |
| C7 `write` scope check tautologied | 6 failed, 89 passed |
| C8 `merge` precedence reversed | 5 failed, 90 passed |
| C9 tuple shape check tautologied | 2 failed, 93 passed |
| **C10 `bindings.json` S_ISREG guard deleted** | **95 passed — SURVIVES (F-20)** |

**My own mutants (all on scratch copies of a repaired passing bundle; baseline
`PASS: S0-06 four-scope - 4/4 assertions, substrate ai-memory 1.39.0@73715b6f` exit 0):**

| # | mutant | verdict | finding |
|---|---|---|---|
| V1 | `binary_sha256` → 64×`a` | **PASS** | F-2 |
| V2 | posture value `"false "` (trailing space) | `substrate: unsafe posture AI_MEMORY_MAINTENANCE__ENABLED=false` rc 1 | exact equality confirmed |
| V3 | `component` renamed + junk `version_stdout` | **PASS** | F-4 |
| V4 | `precedence/raw-team` claims `project: agent--a-alpha` | **PASS** | F-5 |
| V5 | all four raw reads claim `workspace: somewhere-else` | **PASS** | F-5 |
| V6 | merged winner carries the team title+snippet | **PASS** | F-6 |
| V7 | written page's title/kind/tier unrelated to the record | **PASS** | F-7 |
| V8 | `page_path` not derivable from the idempotency key | **PASS** | F-7 |
| V9 | `idempotency_key` replaced wholesale | **PASS** | F-7 |
| V10 | empty recall, tokens in a stray `note` field | **PASS** | F-9 |
| V11 | empty recall, tokens in `scopes_queried` | **PASS** | F-9 |
| V12 | forbidden token in a `_debug` field | `leak: honeytoken HT-team-c52e6f04 surfaced from team` rc 1 | conservative, correct |
| V13 | denied leg: `http-request` (hyphen) | **PASS** | F-8 |
| V14 | denied leg: nested `{"event":{"event":"http_request"}}` | **PASS** | F-8 |
| V15 | denied leg: `HTTP_REQUEST` | **PASS** | F-8 |
| V16 | denied leg: empty event stream | `denied: leg did not record the tuple denial` rc 1 | correct |
| V17 | denied leg: an extra `recall-real.json` sibling | **PASS** | siblings ignored (low) |
| V18 | `confidence: NaN` in both recalls | **PASS** | F-15 |
| V19 | precedence recalls with `records: []` | `precedence: notes/deploy-window.md resolved to <absent>, expected agent` rc 1 | correct |
| V20 | write path listed twice with different `updated_at` | `write: idempotent retry produced 2 records` rc 1 | correct |
| H1–H10 | eight shape mutants + two handled ones | 8 × **traceback, no reason** | F-10 |
| H11 | evidence root is a symlink | **PASS** | F-22 |
| L1–L5 | five `upstream.lock.yaml` mutations | 2 × traceback, 1 × silent last-wins, 1 × PASS on a bumped version | F-3, F-12 |
| G1–G5 | five malformed `/api/v1/search` bodies | 5 × **uncaught** KeyError/TypeError | F-11 |

**Item 4's remaining probes, answered:** "the collision id present in four raw reads but the merged
winner from a *fifth* scope" is **not constructible** — `SCOPE_ORDER` has exactly four members and
`merge` (`:179`) iterates only those, so a fifth-scope record is dropped before it can win (F-14).
"An empty recall whose status is `ok`" is V10/V11 — it **passes** (F-9). "Events written to a sibling
file the checker never reads" is V17 — passes, but the runner writes `denied/events.jsonl` at exactly
the path the checker reads (`collect_leg.sh:126`), so there is no live path to it.

**`authorize` corruption domain — 15 inputs, all correct** (no mutant needed, the boundary holds):
extra field · missing field · `null` for one field · all-null · case variant · trailing space ·
Cyrillic homoglyph in the agent id · list-valued field · dict-valued field · bool · non-dict (list) ·
non-dict (str) → **all denied**; the seed fixture → denied; another actor's real binding → correctly
authorized as `a-gamma`; a row with an extra key → still authorizes (that is `scopes`, by design);
two identical rows → first wins. A row missing a field, a row with an empty-string field, and a
list-valued row field all fail closed after the lane's fix.

**The channel question (item 1) — answered by reading every call site, and it is clean.**
`authorize` has exactly one call site (`factory_memory.py:248`); `load_bindings` exactly one;
`bindings_path` is only ever the module-relative `BINDINGS_PATH` (`:62`) or a constructor argument
with no CLI flag behind it (`_build_parser`, `:408-425`, has none); **zero** occurrences of
`os.environ`/`getenv` in the module. The request body, the query, the record and the environment
reach `authorize` through no path. `bindings.json` resolves via `Path(__file__).resolve().parent`
(`:61`) and `lstat`+`S_ISREG` rejects a directory, a FIFO **and a symlink to the real table**
(reproduced); an absent file raises `FileNotFoundError` uncaught (F-10's class).

---

## 5. Item 5 — the record shapes, re-derived from primary source

`sed -n '1250,1268p' crates/ai-memory-web/src/routes/api.rs` at `73715b6f`:
`struct ApiSearchHit` (line 1254) = `{workspace, project, path, title, kind, snippet, rank: f64}`,
closing brace 1263. **Matches `SEARCH_HIT_KEYS` exactly.**
`sed -n '1170,1190p' crates/ai-memory-store/src/reader.rs`: `pub struct PageSummary` (line 1174) =
`{path, title, kind, tier, updated_at: String}`, closing brace 1185. **Matches `PAGE_SUMMARY_KEYS`
exactly.** The response envelope is a **bare JSON array** (`Json(Vec::<ApiSearchHit>::new())`,
`api.rs:301`), which is what the adapter assumes at `:311`.

Semantics the lane admits it never saw, resolved from source:
- **`rank`** — `f64`, the FTS5 bm25 score; **lower is better** (`search_scopes` keeps the smaller
  rank on a duplicate id and sorts ascending, `api.rs:409-421`). The fixtures use negative values,
  consistent. Sign/range are not asserted anywhere — harmless, since the adapter carries it verbatim
  and nothing compares it numerically.
- **`updated_at`** — `jiff::Timestamp::from_microsecond(updated_us).to_string()`
  (`reader.rs:6022-6030`), i.e. RFC-3339 from the stored column, `unwrap_or_default()` (empty
  string) on an out-of-range value. Deterministic per stored value → see F-24 / D-4.
- **`snippet` vs the page body** — `snippet(pages_fts, 1, '<mark>', '</mark>', '…', 24)`
  (`reader.rs:1483`). 24-token window, `<mark>`-decorated. See F-23; the token cannot sit outside the
  window for the committed canary bodies.

**Seams the runner depends on that the lane did not name, all verified present at the pin** (I
checked these because F-1 made me distrust the runner's seam work): `generate-auth-token` exists and
prints one line (`commands/generate_auth_token.rs:26`); `serve --transport http --bind` exist
(`cli.rs:2121-2125`, default transport is **stdio**, so the flag is load-bearing); `--enable-web` is
**required** for `/api/v1` to exist at all (`split_web_routers` returns empty routers when it is
false, `crates/ai-memory-web/src/mount.rs:317-322`); `/admin/write-page` is merged into the same
router (`commands/serve.rs:1178`) behind `require_dual_auth`, which **accepts a plain root bearer**
(`crates/ai-memory-mcp/src/human_auth.rs:1022-1026`); `write-page` auto-creates the workspace and
project (`create_ws_proj`, `admin.rs:6400`).

---

## 6. Item 8 — the claims boundary. CLEAN.

Grepped the adapter, the checker, `spec.json`, the fixtures, the `s0-13-s0-06-four-scope` row in
`todo/BUILD-TASKLIST.md`, and the S0-06 row at `STATUS.md:45`, for `fubuki|token budget|character budget|
memory_required|minted|result.json|live substrate`. **No over-claim anywhere.**
- `proofs/S0-06/result.json` does not exist at the PIN; `proofs/ledger.json` carries
  `{"classification":"execution_proof","proof_id":"S0-06","state":"ABSENT"}`; `ledger-gen` reproduces
  the committed bytes exactly; `validate-ledger integrity` is rc 0.
- Both rows state "the live leg on a real ai-memory NOT run" and "nothing minted", and both name
  the ADR conflict as an owner decision (the S0-06 status row is `STATUS.md:45`; the ledger row is
  `todo/BUILD-TASKLIST.md:70`).
- Read contract 5 (Fubuki bounds + budget) and the `memory_required` pre-dispatch check are named
  NOT-built in report §8 items 3-4 and appear nowhere in the code. The adapter's module docstring
  (`factory_memory.py:30-32`) explicitly says there is no delete/purge/promote/approve entry point,
  which I confirmed by AST (public surface is `recall` + `write`).
- The lane touched **no attested input** (`proofs/schemas/*`, `scripts/proof-runner`,
  `scripts/validate-ledger`, `proofs/registry.yaml` are all unchanged in `git show --stat 380877b`),
  so AF-AP-56's regeneration gate does not apply.

---

## 7. Item 13 — the design questions

**D-2, which ADR the Stage 0 contract binds: the FOUR-scope one, unambiguously.** Not by preference
— by what the contract documents say. `seeds/seed-stage0-v1.yaml:450-453` lists as S0-06's
assertions "merge precedence Agent->Project->Team->Company" and "a honeytoken staged in one scope
NEVER surfaces in another scope's recall"; the four-row mapping table is
`docs/03_INTEGRATION_CONTRACTS.md:76-81`, and read contract 3 ("Merge with Agent -> Project ->
Team -> Company precedence and deterministic de-duplication") is
`docs/03_INTEGRATION_CONTRACTS.md:86`;
and `proofs/registry.yaml:17` fixes `"assertion_count": 4`. The two-scope ADR
(`docs/adr/0003-two-durable-memory-scopes.md:12`) cannot satisfy a seed assertion about Team, so it
is not the ADR Stage 0 is built against. The lane chose correctly. **The number collision is still a
defect** — two `accepted` ADRs sharing `0003`, both dated 2026-09-02 — and only the owner can retire
one.

**What comes OUT if the owner picks the two-scope ADR** — exactly, by file:
- **Files deleted:** none outright, but `proofs/S0-06/fixtures/evidence-leak/` (22 files) loses its
  point: with only Project and Company, the leak leg's forbidden set (`LEAK_FORBIDDEN = team,
  company`, `check_four_scope.py:44`) collapses to `company` alone, and Company is *authorized* for
  every binding in a two-scope world, so there is no cross-scope boundary left to canary. The leak
  assertion would have to be re-specified as "a `_global` page never surfaces in a project-scoped
  recall", which is a **different** proof.
- **`bindings.json`:** rows 2 and 3 go (`:12-25`); `scopes` shrinks to `["project","company"]`;
  `a-beta` and `a-gamma` disappear, so `fixtures/s0-06/neg-unauthorized-tuple.json` loses the
  `t-platform`/`a-gamma` row it borrows its one wrong field from and must be re-authored.
- **`factory_memory.py`:** `SCOPE_ORDER` and `scopes_for` (`:68`, `:104-111`) lose `agent`/`team`;
  the tuple shrinks from four fields to two (`TUPLE_FIELDS`, `:69`), which changes
  `authorize`'s whole domain and every tuple-corruption test (`tests/…:210`, `:228`).
- **Legs and rows:** the `precedence/` leg needs 2 raw reads not 4, and `check_precedence`'s
  `collisions != 1` / `four distinct variants` rows (`:164`, `:168`) become 2-way; the `write-scope`
  leg's active scope changes from `agent` to `project`; `WRITE_REVIEWED_SCOPES` (`:74`) is unchanged.
- **Rough size:** ~4 of the 12 code files change substantively, 22 of the 56 files are re-purposed
  or dropped, and the seed's own assertion list would have to be amended — which means the seed, not
  just the lane, is downstream of this decision. **That is why report §10's advice is right: do not
  run the PC leg until D-2 is settled.**

**D-3, is `(factory, _global)` a naming hazard worth a rename?** Yes, and I would rename it, but the
strongest argument is narrower than the lane's. What I can cite in source: the reserved scope is
`(DEFAULT_WORKSPACE_NAME, GLOBAL_SCOPE_PROJECT)` = `("default", "_global")`
(`crates/ai-memory-store/src/scope.rs:254-292`; `crates/ai-memory-core/src/lib.rs:28,41`), and
`create_explicit_scope` (`scope.rs:231-244`) has no reserved-name check, so `(factory, _global)` is
created as an ordinary project — the lane's D-3 is correct and I reproduce it. The *consequence* that
decides it: a future operator who runs any ai-memory tooling that addresses the reserved scope (the
MCP `scope: "global"` argument, which refuses to combine with `workspace`/`project` —
`crates/ai-memory-mcp/src/server.rs:6859-6866`) will silently address `("default","_global")`,
a **different, empty** project, and conclude Company memory is empty. A name that cannot be reached
by the substrate's own global-scope affordance should not be spelled like it. `company--factory` is
a poor choice though (it inverts the `<kind>--<id>` convention the other three rows use); the
consistent name is **`company--<company-id>`**, e.g. `company--factory`… which is the same string,
so: fine, but write it as the fourth row of the same convention rather than as a special case, and
change `docs/03_INTEGRATION_CONTRACTS.md:78` in the same increment or the adapter and the contract
diverge. Cost: one line in `scopes_for` (`:110`), one in `seed_scopes.projects_for` (`:50`), one in
`collect_leg.project_for` (`:40`), and the `_global` special case disappears entirely.

**D-3b, is the adapter's own event stream an adequate "no request was made" instrument?**
**No — and I can now say why with a measurement rather than an argument.** The lane's §1.3 reasoning
is *correct as far as it goes*: `/admin/audit-log` (`crates/ai-memory-mcp/src/admin.rs:617`) lists
store **mutation** events, so it cannot witness an absent `/api/v1` **read**. But the instrument the
lane fell back on is the subject's own self-report, which is exactly the thing AF-AP-28 says an
assertion must not rest on — and F-8 shows it is trivially defeated by renaming one string.
Meanwhile **I demonstrated a real second instrument in the sandbox, at a cost of ~15 lines**: a
loopback listener that counts `accept()`s, with a paired positive control that proved the counter
fires (0 accepts for the denial, 2 for an authorized recall on the same port, §3). The PC leg can do
the same for free — the instance is already loopback-only on a port the runner chose, so
`ss -tn state all "dport = :$PORT"` before and after, or simply the instance's own request count if
one is exposed, gives a substrate-side witness. **My recommendation: the PC leg must add one
substrate-side or socket-side instrument to the `denied` leg before this assertion is minted.**
Until then, assertion 1 has *one* instrument, not two, and the `spike_to_class_mapping`'s claim of
two instruments per assertion is true for assertions 2-4 only.

---

## 8. Reproduced vs reviewed vs skipped

**Reproduced (ran it myself):** the S0-06 module twice in the sandbox on `git archive 380877b` and
once on the PC over the bridge (0-byte patch); the three spec negatives and the deferring positive
leg; `report_lint` (both ways); `ap_screen` (both screen versions); `pyflakes`; `bash -n`;
`validate-ledger integrity`; `ledger-gen` + byte compare; 31 of my own checker/adapter/lock/response
mutants; the 10-bug mutation audit of the gate; the lane's red control for the `authorize` fix; the
15-input `authorize` corruption domain; the `bindings.json` path-resolution domain; the merge domain
(same-path-in-one-scope, missing key, NaN/inf/-0.0, out-of-range scope, ties); the paired
accept-counting network control.

**Reviewed statically (read, cross-checked against primary source, not executed):** all three PC
shell scripts and `seed_scopes.py` (the brief forbids running them) — including the F-1 trace, the
token handling, the `stop_instance`/`set -u` interaction, which is safe. The
assignment `RUNDIR="$(mktemp -d ...)"` is `run_s0_06_legs.sh:30`.
The handler install `trap stop_instance EXIT` is `run_s0_06_legs.sh:46`, i.e. after it.
The early return on an absent pidfile is `run_s0_06_legs.sh:36`. So AF-AP-58 does not bite, the readiness wait's two failure exits (68/69), the port
preflight's `exit 65`, and the external-command enumeration; the ai-memory seams (route table, auth
middleware, snippet/timestamp producers, `create_ws_proj`); `seed_scopes.py`'s independence from the
adapter, asserted by **AST** as the brief asks — imports are exactly
`{__future__, argparse, json, pathlib, stat, sys, urllib.request}`, no `importlib`/`exec`/`eval`/
`__import__`, and the only occurrence of the string `factory_memory` is the docstring line saying it
is deliberately independent.

**Skipped deliberately, and why:**
- **Executing `run_s0_06_legs.sh` / `start_ai_memory.sh` / `collect_leg.sh` / `seed_scopes.py`** —
  the brief's explicit prohibition. F-1 is therefore a static trace plus the source's own 404 arm,
  not an executed repro; I give a 30-second falsification recipe in F-1 for that reason.
- **Any cargo build, any ai-memory instance, anywhere** — prohibited, and unnecessary for every
  finding above.
- **The full `tests/` tree** — the lane's own NOT-done #5 (amended on `a449697`). I ran the lane's
  module on both venues; the whole tree executed remains unmeasured by both of us and belongs to the
  coordinator's PC suite.
- **Re-running all 28 lane mutants individually** — I reproduced the class by mutating the checker
  itself (10 injected bugs) and spot-reproduced 6 rows; running the other 22 would have added cost
  without adding information, since the lane's killer lines matched where I checked.
- **`rust-toolchain.toml` / D-5** — I confirmed the file is tracked at the pin
  (`git show 73715b6f:rust-toolchain.toml` → `channel = "1.95"`), so `cargo +1.95.0`
  (`start_ai_memory.sh:63`) is **redundant, not conflicting** (same channel; the override just makes
  the intent explicit and survives the file moving). No finding. The spike artifact's false fact is
  logged by the lane in `docs/INCIDENT-LOG.md` and is outside this lane's boundary.

---

## 9. Shared-tree hygiene and process census

- **Zero writes to `/home/user/agent-factory`.** Every grade ran against
  `git archive 380877b | tar -x` under
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vm1/`; every mutant ran
  on a per-mutant `tar` copy under `…/scratchpad/attack/`. No `stash`/`checkout`/`restore`/`reset`/
  `add`/`commit`/`push`. Read-only git only: `archive`, `show`, `log`, `status`, `rev-parse`,
  `fetch -q`, `worktree add --detach` / `worktree remove --force` (the brief's authorised PC-gate
  path; `git worktree list` now shows only `/home/user/agent-factory` again).
- Other lanes' 27 uncommitted paths (S0-01, S0-08, hooks, tests) were untouched; **none is in my
  scope**. `ap_screen` was run from the PIN copy precisely so another lane's uncommitted
  `edit-snapshot.py` could not colour my classification (I then re-ran it with the shared-tree
  version and got the same 2 + 4 hits).
- Every pytest invocation carried an explicit `--basetemp` under
  `…/scratchpad/basetemp/<name>`.
- **Processes I started, all mine, all gone:** one in-process `ThreadingHTTPServer` on 127.0.0.1
  (ephemeral port 45399, `shutdown()` + `server_close()` in the same process); one raw listening
  socket (port 37219, closed at the end of the same script); one ephemeral bind to read a free port
  (52183, released immediately); ~15 foreground `pytest`/`python`/`bash` subprocesses, all exited.
  Final `ps` shows none of mine alive and `ss -ltn` shows none of my ports listening. **No
  `pkill`/`killall`/`pgrep` was used at any point.** The one `pytest` still running on the box
  (pid 9240, `tests/test_s0_01_frame_tee.py`, basetemp `…/vb14/`) belongs to another verifier lane
  and I left it alone.
- One background escape: my mutation-audit script exceeded the 120 s foreground cap and the harness
  moved it to the background. I did **not** stop — I waited for it in a foreground poll loop and
  read its complete output before continuing.
- **No credential was read, printed or committed.** `.pc-bridge.env` was copied into the detached
  worktree by path only (`cp`), never opened; the honeytokens I handled are the committed synthetic
  canaries.
- Scratch: `…/scratchpad/vm1`, `…/scratchpad/attack`, `…/scratchpad/basetemp` — deleted on
  completion; the report lives at `…/scratchpad/wf-results-r5/VERIFY-M1.md`.
- **`report_lint.py` on this report** (same `--map` set as §0, plus `spec.json`, `bindings.json`,
  `records-precedence.json`):
  `report_lint: 116 refs - OK 34, NEAR 0, MISS 21, UNCHECKABLE 32, UNRESOLVED 29 (at 380877b)`.
  I fixed the 5 citations that were genuinely loose (`bindings.json:20-24` -> the a-gamma row at
  `:19-25`; `docs/03_INTEGRATION_CONTRACTS.md:74-81` -> the table at `:76-81` plus read contract 3 at
  `:86`; the `STATUS.md`/ledger conflation; the `RUNDIR`/`trap` sentence; `"assertion_count": 4`),
  which took MISS from 26 to 21. **I then hand-checked the line number behind every one of the
  remaining 21 and all are correct** - they are the linter's known heuristic shape: a report line
  carrying two refs has each ref graded against *all* claim tokens on that line, so e.g.
  `factory_memory.py:304` MISSes because the same sentence also names `:307`. Three more
  (`report:44`, `:69`, `:72`) are the tool linting its own output pasted inside my sec 0 block.
  The 29 UNRESOLVED are all `crates/...` paths from the pinned ai-memory checkout, which does not
  exist at any revision of this repo; I verified each of those by `sed -n` against
  `/home/user/nerdherderdani/ai-memory` at `73715b6f` (confirmed
  `git rev-parse HEAD` = `73715b6f1b2f0abb0a8b0ed47c1f69b1bd1b806e`) instead.

---

## 10. VERDICT — NOT-READY

**Blocking set (1):**
- **F-1** — the PC leg runner cannot complete: the leak leg queries `agent--a-beta`, seeding creates
  `agent--a-alpha`. Two independent failures on the same wiring. **This is a two-line fix.**

**Fix-before-capture set (5)** — not blocking the merge of the code as landed, but each one turns a
PC capture into evidence that has to be re-taken if it is fixed afterwards, and re-capture is the
expensive step:
- **F-2** substrate digest compared to nothing · **F-5** raw instruments' own provenance unread ·
  **F-8** one-string denylist for "no request" · **F-9** empty recall satisfies the vacuity oracle ·
  **F-10** eight shapes crash without a reason.
Add **D-3b** (assertion 1 has one instrument, not two) — it needs a decision, and if the answer is
"add a socket-side witness", that changes `collect_leg.sh`, i.e. it must land before capture too.

**Everything else (F-3, F-4, F-6, F-7, F-11 … F-26)** is hardening and honesty-of-record; F-6, F-7
and F-11 are the ones I would take next, in that order.

**What is genuinely good, and I say so having tried to break it:** the authorization boundary is the
strongest part of this lane — 15 corruption inputs, a clean channel analysis (one call site, no
`os.environ`, no CLI override), a real red control, and a denial proven to precede the connect with a
*counting* instrument and a paired positive control. `merge` is order-independent, clock-free and
non-mutating, and nine of my ten injected bugs were caught by the lane's own suite. The report's
NOT-done section is honest and complete, the PROVENANCE files label every synthetic value, and
nothing is minted or claimed.

### Cheapest path to MERGE-READY

1. **F-1's two-line seeding fix** + the wiring regression test in F-1 (~20 min, sandbox-only).
2. **F-9 (2 lines), F-8 (1 line), F-2 (rename + comment), F-10 (5-line wrapper + 1 REASONS row)**
   and **F-5's provenance loop (~4 lines, reading the `tuple.json` the runner already writes)** —
   all sandbox-testable against the committed hostile bundles, each with the red test named above
   (~90 min total).
3. Re-run `scripts/lane_gate.sh` on the new bytes; expect the count to rise from 95 by the number of
   new tests. Then the PC gate.
4. **Owner decision on D-2** — the four-scope ADR is what Stage 0 binds (§7), but the two accepted
   `0003` files must be resolved before the PC leg runs, because a two-scope answer re-specifies the
   leak leg rather than trimming it.
5. Only then capture on the PC.

### Exact PC steps for the coordinator's live leg — what must be true before `run_s0_06_legs.sh` may run

**Preconditions (all of them, in order):**
1. D-2 settled toward the four-scope ADR (else stop — report §10's own advice, which I endorse).
2. F-1 fixed and pushed; the sandbox gate green on the new bytes.
3. `scripts/pc.sh` reachable this session (a fresh BRIDGE READY banner in `.pc-bridge.env`).
4. The PC clone ff-synced to the commit carrying the fix
   (`git -C /home/rocco/agent-factory fetch && git -C … checkout <sha>`), because
   `check_four_scope.py:37` reads `upstream.lock.yaml` from `parents[2]` of its own path.
5. **Port 48606 free on the PC** — the script refuses with `exit 65` rather than squatting, which is
   correct; confirm with `scripts/pc.sh 'ss -ltn "sport = :48606"'` first so a refusal is not
   mistaken for a failure.
6. **`~/s0-06-pinned/ai-memory` must not be a checkout anyone is using** (F-19) — the script
   force-detaches it. Either confirm it is absent, or pass an explicit `S0_06_SRC` under a scratch
   path.
7. Disk: the wave-0 spike measured **618 MB + 306 MB** of built binaries plus a full `target/`.
   Confirm free space on the PC before the build.
8. Toolchain: `cargo +1.95.0` must resolve on the PC (rustup 1.95.0 is installed per `PC-BRIDGE.md`);
   the pinned `rust-toolchain.toml` already says `channel = "1.95"`, so the override is redundant but
   harmless.

**Run:**
```
scripts/pc.sh 'cd /home/rocco/agent-factory && bash proofs/S0-06/tools/pc/run_s0_06_legs.sh'
```
It starts its own instance on 127.0.0.1:48606 with a fresh temp data dir and a run-scoped 0600
token, seeds, captures four legs, stops **its own pid** after confirming `/proc/<pid>/exe`, and
grades. It never touches the owner's OmniRoute / Buzz relay / Ollama / Phoenix / OpenObserve / neo4j.
The build alone will exceed the bridge's 120 s per-call budget — run it the way `pc_lane.sh`
runs long jobs (setsid + redirect + poll), **not** as one blocking bridge call.

**After a green grade:**
```
python3 scripts/proof-runner run --proof S0-06 --venue pc-bridge --root .
python3 scripts/validate-ledger integrity --root . && python3 scripts/ledger-gen --root . \
  && git diff --exit-code proofs/ledger.json
shred -u <RUNDIR>/token <RUNDIR>/curl.cfg      # F-18 — the runner keeps them today
```
and **never commit the run dir or `proofs/S0-06/evidence/`'s token-bearing siblings.**

**Do not mint** if the grade is `deferred:` (exit 2) or if any leg needed a hand edit — F-2 through
F-10 mean a hand-edited bundle is cheap to fake and the checker will not notice.

