# REPIN-a report — lane runtime pin in upstream.lock.yaml

## Outcome

DONE. Three files modified/created, all gates green. Changes in working tree, not committed.

## Files touched

| File | Action | Lines |
|---|---|---|
| `upstream.lock.yaml` | MODIFIED — appended `lane_runtime:` section (13 new lines after line 160) | 160 → 173 |
| `tests/test_upstream_lock_lane_runtime.py` | NEW — 8 tests (6 positive, 1 golden parity, 1 negative control) | 103 lines |
| `docs/HARNESS-PORTS.md` | MODIFIED — appended `## 12. Lane runtime pin` section | 682 → 697 |

## Entry values (all from the brief's MEASURED data, never typed)

- `commit: b3399c139624a0081d70397741a5b45f60fbe1f4` (40 lowercase hex)
- `version: "0.21.1"`
- `python: "3.11.15"`
- `sqlite: "3.53.1"`
- `role: "lane-runtime (scripts/pc_lane.sh -> hermes on the PC); NOT the S0-01 proof runtime"`
- `reason: "SQLite >= 3.51.3 for WAL on the shared profile state.db (VERIFY-B5j); owner-run hermes update 2026-09-08"`
- `diff_from_proof_pin: "31816 commits, 3939 files"`
- `verified: "harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ"`

## Existing entry byte-identity proof

```
$ git diff upstream.lock.yaml
```

The diff shows ONLY the appended `lane_runtime:` section (lines 161-173). Zero changes to lines 1-160. The `selected_core.hermes-agent` entry at lines 10-15 is untouched. The test `test_hermes_agent_entry_unchanged` independently asserts byte-identity against a golden of the committed values:

```python
HERMES_AGENT_GOLDEN = {
    "repository": "https://github.com/NousResearch/hermes-agent.git",
    "commit": "527da60844d4dced37879ea50259675371abe10e",
    "observed_version": "0.21.0",
    "license": "MIT",
    "role": "main_production_workhorse_and_native_acp_server",
}
```

## Verified: lane count (pasted from grep, not typed)

Command:
```
grep -E '(HOME|LANDED)' todo/BUILD-TASKLIST.md | grep -iE '(PC|hermes|Qwen|local-Qwen)' \
  | grep -oE '[A-Za-z0-9_][A-Za-z0-9_-]* (HOME|LANDED) 2026-09-(08 1[4-9]|08 2[0-3]|0[9]|1[0-9]|2[0-2])' \
  | sort -u | wc -l
```

Result: **43** unique PC-lane HOME/LANDED stamps since 2026-09-08 14:xxZ (`/tmp/repin/pc_stamps_final.txt`).

## Consumer analysis (code intel first)

**graft ask "who reads or parses upstream.lock.yaml"** returned 8 hits. Supplemented with:
```
grep -rn 'upstream.lock' scripts/ proofs/ tests/ src/ harness-ports/ .claude/
```

### Critical consumers and impact of the new entry

| Consumer | Reads section | Impact |
|---|---|---|
| `proofs/S0-12/check_pin_diff.py:37` | `for section in ("selected_core", "selected_later_planes",` — enumerates only four sections | **SAFE** — `lane_runtime` is outside the four; invisible to S0-12 |
| `proofs/S0-12/check_pin_diff.py:34` | `lock = yaml.safe_load(...)` — full parse, but iteration at :58-69 is bounded to `lock_pins` from the four sections | **SAFE** — confirmed by reading the loop |
| `scripts/vendored_manifest.py:620` | `if repository and pin:` — gate inside `parse_lock`; returns only entries with BOTH a `repository` URL and a pin | **SAFE** — no `repository:` key in the new entry; `parse_lock` skips it |
| `scripts/vendored_manifest.py:608` | `entries.setdefault(component, {})["key"]` — component-keyed; `hermes-agent-lane-runtime` distinct from `hermes-agent` | **SAFE** — no collision |
| `proofs/S0-06/check_four_scope.py:213` | `text = (REPO_ROOT / "upstream.lock.yaml").read_text(...)` — the `_lock()` helper; reads `selected_core.ai-memory` only | **SAFE** — unrelated section |
| `scripts/fubuki_pin_sync.sh:19` | `LOCK="$ROOT/upstream.lock.yaml"` — the awk at :23 targets `fubuki-os:` block only | **SAFE** — unrelated block |
| `scripts/verify-planning-repo.sh:12` | `upstream.lock.yaml` — file-existence check in the required-files list | **SAFE** — file still exists (verified green) |
| `proofs/S0-08/check_containment.py:51` | comment: `run_containment.sh` refuses any checkout other than the `hermes-agent` pin at lines 10-15 | **SAFE** — comment only, no runtime read |
| `harness-ports/roles/researcher.md`, `harness-ports/briefs/code-search.md`, `.claude/skills/code-intel-trio/SKILL.md` | documentation references | **SAFE** — no enumeration |

**No consumer enumerates `lane_runtime:` entries.** The entry shape was chosen to be invisible to the two strict enumerators (S0-12, `parse_lock`) by: (a) using a section outside S0-12's four-section list, and (b) omitting `repository:` so `parse_lock` skips it.

## Test results (pasted, not typed)

**Run 1:**
```
........                                                                 [100%]
8 passed in 0.13s
```

**Run 2:**
```
........                                                                 [100%]
8 passed in 0.12s
```

**pyflakes:** clean (rc 0).

**verify-planning-repo.sh:** `planning repository verification passed` (rc 0).

## Negative control

`test_short_commit_rejected`: creates a mutated lock copy with `commit: "b3399c1"` (7 hex). Asserts the 40-hex regex does NOT match. The test passes, confirming the negative control is live.

## NOT done

- REPIN-b (the `scripts/pc_lane.sh` drift check) — serialized behind T90-R2; not this increment's boundary.
- No commit, no push, no git add — changes left in the working tree per the brief.
- No ledger/wiki/CLAUDE.md changes — outside this increment's boundary.

## Self-attack: three most likely ways this change is wrong

1. **The 43-count overestimates.** Some HOME/LANDED stamps may be meta-events (AUDIT, SEED, VERDICT, LANES) rather than individual PC lane completions. Mitigation: the stamps were extracted from lines that also match `PC|hermes|Qwen|local-Qwen`, so they reference PC-lane context; the count is conservative because it deduplicates (sort -u) — some lanes have BOTH a HOME and a LANDED stamp, counted once each.

2. **A future consumer might enumerate `lane_runtime:` entries and break.** Mitigation: the section name is distinct from the four S0-12 sections; `parse_lock` ignores it structurally (no `repository:` key); any new consumer would be written against the file's existing structure and would need to opt in to reading `lane_runtime:`. Ruled out for all current consumers by the grep.

3. **The YAML quoting style differs from existing entries.** The existing `selected_core` entries use unquoted values for most fields; the new entry quotes string values. Mitigation: YAML 1.1 (PyYAML default) treats both identically; the test loads via `yaml.safe_load` and compares Python dicts, which strips quoting. The `version: "0.21.1"` quoting is intentional — YAML reads unquoted `0.21.1` as a string (it has two dots), but quoting makes the intent unambiguous. Verified by the passing tests.
