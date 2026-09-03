---
topic: incident-lessons
last_compiled: 2026-09-03
---

# Incident Lessons — anti-pattern registry, operational lessons

## 1. Purpose [coverage: high -- 5 sources]

This topic distills the project's incident log and anti-pattern registry into searchable
operational knowledge. Every rule in CLAUDE.md traces to an incident; every incident registers
its anti-pattern class. The registry IS the sweep corpus for the next `/bug-echo` run.

Full log: [docs/INCIDENT-LOG.md](docs/INCIDENT-LOG.md).

## 2. Architecture [coverage: medium -- 3 sources]

**Anti-pattern registry** (AF-AP-* rows in `docs/INCIDENT-LOG.md`):

| ID | Mechanism | Proven instance | Status |
|---|---|---|---|
| AF-AP-1 | Total-isolation instrument as selective-egress negative control | Chairman netns probe: `unshare --net` blocks both legs | OPEN until spike #6 |
| AF-AP-2 | Collective reference satisfying per-item gate | Seed self-validation red: 6 proof ids appeared once | SWEPT |
| AF-AP-3 | Uncommitted work at multi-agent dispatch boundary | Council agents dispatched with findings uncommitted; container restarted | SWEPT |
| AF-AP-4 | Sandbox-probe-as-world venue classification | Findings classified S0-08/S0-03 as blocked while PC had the capability | SWEPT |
| AF-AP-5 | Orphaned lines past top-level exit | post-commit had dead `slopo` block after `exit 0` | SWEPT |

The registry also inherits the source repo's AP-1..AP-70 signatures in the edit-snapshot hook's
AP_SCREEN (mechanical tells only).

**Incident entries (full detail in the log):**
1. Sandbox-only world while PC bridge existed (2026-09-03) -- Phase-1 environment inventory bite
2. GitNexus timeout on 3.8k-file tree (2026-09-03) -- run analyze detached
3. Chairman probe falsified S0-05 mechanism (2026-09-02) -- AF-AP-1
4. Seed self-validation red (2026-09-02) -- AF-AP-2
5. Ouroboros stdio quirks (2026-09-02) -- IS_SANDBOX, initial_context cap, metacharacters
6. Uncommitted doc at council dispatch (2026-09-02) -- AF-AP-3
7. Owner term "quartet" misread as git hooks (2026-09-03) -- grep owner source repo first
8. Batch A syntax error in post-commit (2026-09-03) -- AF-AP-5
9. Batch D silent except sites (2026-09-03) -- AP-24 from source repo, caught by delta gate

## 3. Talks To [coverage: medium -- 3 sources]

- Incidents --> CLAUDE.md rules (general lessons baked into matching section/skill)
- Anti-pattern registry --> edit-snapshot hook AP_SCREEN (mechanical signatures)
- `/bug-echo` --> registry (sweep corpus for sibling detection)
- Pre-commit hook --> lint_delta.py (delta gate that caught batch D's AP-24)

## 4. API Surface [coverage: low -- 1 source]

Not applicable -- the registry is a document, not code. The mechanical interface is the
edit-snapshot hook's `AP_SCREEN` dictionary, which contains greppable signatures for automated
detection during edits.

## 5. Data [coverage: medium -- 2 sources]

- `docs/INCIDENT-LOG.md`: full incident detail + anti-pattern registry table
- `.claude/hooks/edit-snapshot.py`: AP_SCREEN signatures (mechanical subset)
- `tests/test_shell_syntax.py`: regression gate for AF-AP-5

## 6. Key Decisions [coverage: high -- 4 sources]

- Owner mandate (inherited 2026-08-20/21/22): every real defect gets `/bug-echo` run and
  registered BEFORE the increment closes -- part of the light loop, not just deep-mode Phase 5
- Every new registry row with a mechanical signature extends the edit-snapshot AP_SCREEN
- General rules from incidents baked into matching SKILL; the log carries incident detail
- A delta gate on a wholesale port is a full-tree audit in disguise -- budget for it
- Owner term of art: grep the owner's source repo before interpreting

## 7. Gotchas [coverage: medium -- 3 sources]

**NOT-built (first-class):**
- The registry has 5 entries (AF-AP-1..5); the source repo's inherited set (AP-1..70) is in the
  hook screen but not re-proven in this repo
- AF-AP-1 is OPEN (selective egress mechanism not yet built)
- No `/bug-echo` sweep has been run over this repo's own code (all entries are from the setup
  port and pipeline work)

**Operational lessons (apply before they bite again):**
- Commit before any multi-agent dispatch (AF-AP-3)
- Run environment inventory from the owner's live assets, not sandbox alone (AF-AP-4)
- Shell syntax gate catches invisible errors past `exit 0` (AF-AP-5)
- GitNexus analyze outlives 240s Bash cap on this tree -- always detached
- Ouroboros: IS_SANDBOX=1, initial_context < 1.5k, sanitize metacharacters

## 8. Sources

- [docs/INCIDENT-LOG.md](docs/INCIDENT-LOG.md)
- [CLAUDE.md](CLAUDE.md)
- [.claude/hooks/edit-snapshot.py](.claude/hooks/edit-snapshot.py)
- [tests/test_shell_syntax.py](tests/test_shell_syntax.py)
- [docs/research/FINDINGS-STAGE0-v1.md](docs/research/FINDINGS-STAGE0-v1.md)
