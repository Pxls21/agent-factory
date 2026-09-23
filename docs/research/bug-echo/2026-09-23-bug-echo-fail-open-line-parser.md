# bug-echo Report: fail-open line parser of a structured file (AF-AP-25, the silent-skip twist)

**Date:** 2026-09-23
**Pattern source:** user-described (the coordinator), from VERIFY-REPIN-a F11 (`tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md` §8)
**Scan tool:** regex (the Grep tool and `grep -rn`), then a per-site read of every candidate
**Files scanned:** the first-party gate and tool paths: `scripts/`, `scripts/hooks/`, `harness-ports/bin/`, `proofs/`, `src/`, `.github/` (Python and shell; tests and `proofs/**/archive/` excluded)
**Pattern validated:** n/a for described mode. The origin was reproduced dynamically instead (below).
**Output dir:** `docs/research/bug-echo/` (the house convention in `.agents/lane-skills/bug-echo/PROJECT-NOTES.md`)
**Autonomous choices (the project forbids blocking questions):** pre-flight found two uncommitted files, a live lane's report and the coordinator's CLAUDE.md edit; the scan only reads, so it proceeded. The breadth guard fired (36 raw line loops); the pattern was tightened to loops that parse a structured config, lock, allowlist or registry file, leaving 20 candidate sites, each classified below (2 BUG, 1 WATCH, 15 OK, 2 REVIEW). Step 6's guided fix is not taken here: both BUG sites go to task #170 as one build increment with red-first tests.
**Semantic-sibling amplifier:** slopo unavailable in this workspace; grep and per-site reading only.

## Pattern

**Anti-pattern:** a hand-written loop over the lines of a structured file matches each line against a few regexes and IGNORES any line that matches none of them. A line in a form the regexes do not spell out (a trailing space, a YAML comment, a quoted value) silently drops data, or silently re-attaches the next lines to the previous record. The gate that consumes the parse keeps passing over a smaller set.

**Correct pattern:** parse with a real parser (`yaml.safe_load`, plus a duplicate-key refusal where duplicates matter), or refuse every non-blank, non-comment line the loop does not recognise, by line number. `harness-ports/bin/qwen-matrix.sh:113` (`while IFS= read -r line`) is an in-repo example of the second form: an unknown baseline line sets rc 8.

**Search regex:** `for [a-z_, ]+ in (enumerate\()?[^#]*(splitlines\(\)|readlines\(\)|open\()` for Python and `while (IFS=[^ ]* )?read` for shell. Each hit was then read and kept only if the file it parses is structured config, not JSONL evidence (parsed with `json.loads`, which raises), command output or a log.

## Reproductions (the coordinator, 2026-09-23 08:5xZ, scratch copies only)

- **Origin, `parse_lock`:** one trailing space on the `  hermes-agent:` line of a copy of `upstream.lock.yaml` → `parse_lock` returned 23 pins instead of 24, `selected_core.hermes-agent` gone, no error.
- **Sibling, `parse_sbom`:** a YAML trailing comment on the second `- name:` line of a copy of `SBOM.yaml` (`  - name: hermes-agent  # note`, the same document to `yaml.safe_load`) → 21 entries instead of 22; the agent-client-protocol pin DROPPED, and hermes-agent's repository and pin re-attached to the name `agent-client-protocol`. `yaml.safe_load` still reads all four names correctly.

## Summary

- BUG findings: 2
- WATCH findings: 1
- OK findings: 15
- REVIEW findings: 2

## BUG Findings

### Issue Rating Table

| # | Finding | Urgency | Risk: Fix | Risk: No Fix | ROI | Blast Radius | Fix Effort | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | `parse_lock` skips unrecognised lock lines; a pin drops out of `validate_pin_agreement` (the origin, F11) | 🟡 HIGH | ⚪ Low | 🟡 High | 🟠 Excellent | ⚪ 1 file | Small | Open (task #170) |
| 2 | `parse_sbom` skips unrecognised SBOM lines; a pin drops and another is mis-named | 🟡 HIGH | ⚪ Low | 🟡 High | 🟠 Excellent | ⚪ 1 file | Small | Open (task #170) |

### Detailed findings

**1. `parse_lock` — the origin**

`scripts/vendored_manifest.py:592` (`parse_lock(path: Path)`)

```python
        match = re.fullmatch(r"  ([a-z0-9][a-z0-9-]*):", line)
        if match:
            component = match.group(1)
            entries.setdefault(component, {})["key"] = f"{section}.{component}"
            continue
        match = re.fullmatch(r"    (repository|commit|binary_sha256|asset_sha256):\s*(.+)", line)
        if match and component:
            entries[component][match.group(1)] = match.group(2).strip().strip('"')
        elif line.startswith("    ") and ":" not in line:
            raise ManifestError(f"upstream lock parse failure at line {line_number}")
```

**Why this is a bug:** a component line that is not exactly two spaces, a name and a colon (a trailing space, a trailing comment, three spaces) matches neither pattern and is skipped. The component's `repository:` and `commit:` lines then attach to the PREVIOUS component, so one pin vanishes from the pin-agreement check that runs in the pre-commit and pre-push hooks, and the check still says OK. The lock is hand-edited, and J1-4 (task #121) is about to add rows.
**Suggested fix:** parse the lock with `yaml.safe_load` and a loader that refuses duplicate keys, or keep the line parser and raise `ManifestError` on every non-blank, non-comment line it does not recognise. Red-first tests: a trailing space, a trailing comment, a three-space indent and a duplicate component each refused by line number.

**2. `parse_sbom` — the sibling in the same file**

`scripts/vendored_manifest.py:625` (`parse_sbom(path: Path)`)

```python
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = re.fullmatch(r"\s*- name:\s*(\S+)\s*", line)
        if match:
            finish()
            current = {"name": match.group(1)}
            continue
        match = re.fullmatch(r"\s+(repository|commit|digest):\s*(\S+)\s*", line)
        if match and current:
            current[match.group(1)] = match.group(2).strip('"')
        elif line.lstrip().startswith("-") and current and "name:" not in line:
            raise ManifestError(f"SBOM parse failure at line {line_number}")
```

**Why this is a bug:** the refusal branch excludes exactly the lines that start a new entry (`"name:" not in line`), so a `- name:` line with a trailing comment is skipped and the next entry's fields land on the previous one. Reproduced above: one pin dropped, one mis-named, no error.
**Suggested fix:** the same as finding 1, in the same increment: one parsing rule for both files.

## WATCH Findings (near-threshold, defensive only)

### Issue Rating Table

| # | Finding | Urgency | Risk: Fix | Risk: No Fix | ROI | Blast Radius | Fix Effort | Status |
|---|---|---|---|---|---|---|---|---|
| 3 | The provenance-table walk stops at the first line not starting with `\|` | ⚪ LOW | ⚪ Low | 🟢 Medium | 🟢 Good | ⚪ 1 file | Trivial | Open |

**3. Provenance table walk**

`scripts/vendored_manifest.py:506` (`if not line.startswith("|"):`, followed by a break)

**Why this is WATCH not BUG:** a table row with a leading space ends the table early and drops every row after it, but the later declared-roots cross-check ("declared roots absent from provenance") refuses the truncated result, so the gate fails closed today through a second check.
**Suggested fix (defensive, not urgent):** end the table only at a blank line or a heading, and refuse a non-row line inside it by line number; fold into task #170 if it stays small.

## OK Findings (intentional, no action needed)

- `scripts/no_laya_in_gates.py:445` (`for line in text.splitlines():`) — every non-blank, non-comment allowlist line becomes an entry; nothing is skipped.
- `scripts/check-proof-status.py:238` (`for line in text.splitlines():`) — a scan of a mixed prose-and-table document; a missing or doubled canonical row fails closed (exactly one row per tracked proof).
- `scripts/vendored_manifest.py:330` (`lines = data.decode("utf-8").splitlines()`) — the kit index raises on every malformed line (the correct pattern).
- `scripts/vendored_manifest.py:417` (`lines = text.splitlines()`) — the class file raises on every malformed line (the correct pattern).
- `harness-ports/bin/qwen_matrix.py:199` (`for raw in text.splitlines():`) — Prometheus text; every required metric is checked after the loop.
- `harness-ports/bin/qwen-matrix.sh:113` (`while IFS= read -r line`) — an unknown baseline line sets rc 8 (the correct pattern).
- `harness-ports/bin/omniroute_local_builder.py:86` (`for raw in path.read_text().splitlines():`) — a single-key lookup; a missing key returns None to the caller.
- `proofs/S0-01/tools/scripted_backend.py:426` (`for line in path.read_text().splitlines():`) — a single-key lookup that raises when the key is missing.
- `proofs/S0-04/tools/pc/capture_leg.py:70` (`for line in file.read_text().splitlines():`) — a single-key lookup that raises when the key is missing.
- `scripts/realleg_sync.sh:38` (`while read -r sha path; do`) — the whole manifest is diffed against the pulled tree afterwards.
- `scripts/push_clean.sh:25` (`ALLOWED=$(grep -v "^#" .lanes-live`) — the `.lanes-live` set is compared by exact path; a malformed entry refuses the push.
- `proofs/S0-05/check_egress.py:250` (`enumerate(path.read_text().splitlines(), start=1)`) — JSONL; `json.loads` raises on a malformed line.
- `proofs/S0-06/check_four_scope.py:372` (`_read_text(root, "%s/%s" % (leg, name)).splitlines()`) — JSONL; a malformed line raises a named failure.
- `proofs/S0-01/pins.py:553` (`enumerate(_utf8(data).splitlines(), 1)`) — JSONL; a malformed line raises a named failure.
- `src/agent_factory/governance/review.py:91` (`for line in listing.stdout.splitlines():`) — gpg's colon listing; unknown record types are ignored by the format's design, and the key count is checked by the caller.

## REVIEW Findings (need human judgment)

- `harness-ports/bin/sync-skills.sh:60` (`while read -r hash name rest; do`) — the recorded-hash loader skips a line with no hash; what the drift check does for a skill with no recorded hash was not traced. The file is tool-written.
- `proofs/S0-01/tools/build_capture_record.py:39` (`for line in text.splitlines():`) — lines before the first section header are not part of any section hash; whether that preamble can carry evidence was not traced.

## Registry and screen

The class is AF-AP-25 (a regex-list parse where a parser is required); these are its first instances on a pin-agreement gate, with the fail-open-on-unrecognised-line twist. The registry row gains the instances in the same commit as this report. The edit-snapshot screen (`.claude/hooks/edit-snapshot.py`) is not extended here: `.claude/` edits wait for task #150, and the screen line is listed there.
