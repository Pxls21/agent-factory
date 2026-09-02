# GitNexus — use it (MCP → stdio → CLI)

Running **GitNexus** (graph-powered code-intelligence / blast-radius analysis) in a throwaway
container such as *Claude Code on the web*.

> **Operating decision (updated 2026-06-25): use the richest interface that works, in this order —
> native MCP tools, then stdio, then this CLI.** The native MCP is flaky here (loads only at session
> start, often doesn't reconnect after a reclaim), but the *server itself is fine* — so when the
> session integration is down, drive the same 17 tools over **stdio** before falling to the CLI. All
> three satisfy CLAUDE.md's "impact before edits, detect-changes before commits" rule.

## Tier 2 — stdio fallback (`scripts/gn_mcp.py`)

When the native MCP tools are disconnected, talk to the server directly over stdio:

```bash
python scripts/gn_mcp.py --list                                                  # the 17 tools
python scripts/gn_mcp.py impact '{"target":"<symbol>","direction":"upstream","summaryOnly":true}'
python scripts/gn_mcp.py context '{"name":"<symbol>"}'
python scripts/gn_mcp.py detect_changes '{"scope":"compare","base_ref":"<commit>"}'
```

**The gotcha that makes naive stdio probes fail:** a tool call runs an *async* graph query, but a
one-shot `subprocess.run(..., input=...)` closes stdin immediately; the server reads EOF as a client
disconnect and shuts down *before* answering, so you get an empty/"no response" result even though
`tools/list` (synchronous) worked. `gn_mcp.py` keeps stdin open and `select()`-reads until the
response arrives. (`tools/list` works regardless — use it to confirm the server is alive.)

- Tool: [`gitnexus`](https://github.com/abhigyanpatwari/GitNexus) — index a codebase into a knowledge
  graph; query via MCP **or CLI**. Local-first, no upload. 14 languages (Python, TS/JS, Java, Go, …).
- **Verified**: 2026-06-25, agent-distiller sandbox, `gitnexus@1.6.8` (server), stdio + CLI both
  exercised (`impact` on a freshly-indexed symbol returns blast radius). Earlier: 2026-06-20, `1.6.7`.

## Invocation — two forms

```bash
# This repo (and any repo with a committed/indexed .gitnexus/): use the BUNDLED runner.
# No network, fastest, exact pinned build:
node .gitnexus/run.cjs <command> [args]

# A repo WITHOUT a bundled runner: fetch a pinned build via npx (needs npm egress):
npx --yes gitnexus@1.6.7 <command> [args]
```

All examples below use `node .gitnexus/run.cjs`; swap in `npx --yes gitnexus@1.6.7` if there's no
bundled runner.

> Status legend: ✅ verified in this sandbox · 📄 from `--help`, not yet exercised here.

---

## 1. Prereqs ✅

- **Node** present (had v22.22.2) and `npx` on PATH.
- Network reachable to `registry.npmjs.org` (npm install works).
- **No global install needed** — invoke via `npx` with a pinned version so the
  exact build is reproducible across sandboxes.

Quick check:

```bash
node -v && npm -v && command -v npx
```

## 2. Index a repo ✅

```bash
# (Re)index the current repo. Re-run after code changes before impact/detect-changes.
node .gitnexus/run.cjs analyze        # this repo (bundled runner); ~seconds
# npx --yes gitnexus@1.6.7 analyze .  # a repo without a bundled runner

# Inspect what's indexed
node .gitnexus/run.cjs status     # index status for current repo (says "stale" when behind HEAD)
node .gitnexus/run.cjs list       # all indexed repos (global registry)
```

Note: `analyze` **auto-edits the index-count line** in CLAUDE.md / AGENTS.md (inside the
`gitnexus:start` blocks) — expect those two files to show as modified; commit them as a chore.

- The index is written to **`./.gitnexus/`** (~18M here). It is **regenerable**,
  so add it to `.gitignore` rather than committing it:

  ```gitignore
  .gitnexus/
  ```

- The graph is a **snapshot**. Re-run `analyze .` after code changes before
  doing impact/detect-changes, or the analysis will be stale.

## 3. Known caveat in locked-down sandboxes: FTS extension ✅

`analyze` may log:

```
GitNexus: FTS extension unavailable ... INSTALL fts failed ... HTTP Returns: 403,
Failed to download extension "fts" from extension.ladybugdb.com/...
```

This only disables **full-text / BM25 search**. The graph features used for
blast-radius review (`impact`, `context`, `detect-changes`, `cypher`) work fine
without it. To enable FTS when the network allows:

```bash
GITNEXUS_LBUG_EXTENSION_INSTALL=auto npx gitnexus@1.6.7 analyze .
# or, on an already-indexed repo:
npx gitnexus@1.6.7 analyze --repair-fts
npx gitnexus@1.6.7 doctor          # show runtime capabilities + embedding config
```

## 4. Reviewing a change — blast radius ✅

The CLAUDE.md workflow, all via CLI. **`analyze` first if the index is stale** (`status` tells you) —
`impact`/`detect-changes` read the indexed snapshot, so new symbols are invisible until re-analyzed.

```bash
# Blast radius of one symbol: what breaks if you change it (run BEFORE editing it)
node .gitnexus/run.cjs impact <symbol> --summary-only      # counts + risk only
node .gitnexus/run.cjs impact <symbol> -d upstream         # dependants (default)
node .gitnexus/run.cjs impact <symbol> --file <path> --kind Function   # disambiguate a common name

# Map a git diff to impacted symbols + execution flows (run BEFORE committing)
node .gitnexus/run.cjs detect-changes                       # default scope: unstaged (working tree)
node .gitnexus/run.cjs detect-changes -s staged            # staged
node .gitnexus/run.cjs detect-changes -s all               # staged + unstaged
node .gitnexus/run.cjs detect-changes -s compare -b main   # HEAD vs a branch/commit

# 360° view of a symbol: callers, callees, processes it participates in
node .gitnexus/run.cjs context <name>

# Concept search across execution flows / raw graph query
node .gitnexus/run.cjs query "<concept>"
node .gitnexus/run.cjs cypher "<cypher query>"
```

**Diff-scope semantics (verified):** `detect-changes` maps git *diff hunks* to symbols, so the scope
mirrors git — `unstaged` = working tree vs index, `staged` = index vs HEAD, `all` = both, `compare
-b <ref>` = HEAD vs `<ref>`. Commit your change first, then `-s compare -b <pre-change-commit>` to
review the whole increment's blast radius.

**Worked example** (the increment-2 review, 2026-06-20):

```text
$ node .gitnexus/run.cjs impact classify_assertion --summary-only
{ "impactedCount": 3, "risk": "LOW",
  "summary": { "direct": 1, "processes_affected": 2, "modules_affected": 2 },
  "affected_processes": [ { "name": "validate_episodes", ... } ] }

$ node .gitnexus/run.cjs detect-changes -s compare -b f045713
Changes: 21 files, 52 symbols   Affected processes: 13   Risk level: high
Affected execution flows:
  • Validate_episodes  → _is_safe_command  — changed: derive_gate_from_trace, classify_assertion
  • Register_from_episode → _specificity   — changed: derive_gate_from_trace, _candidates, _specificity
  ...
```

*Reading it:* the code blast radius is confined to `validate_episodes` + `register_from_episode` (the
two consumers of `derive_gate_from_trace`) — exactly as expected. The headline `Risk: high` was
inflated by the doc churn in the same compare (markdown headers count as "symbols"); scope to code
files or read the flow list, don't trust the one-word risk blindly.

## 5. MCP wiring (optional — and flaky here)

You do **not** need this; §4's CLI does everything. MCP only matters if you want the graph as live
agent tools. In Claude Code on the web it's unreliable: MCP servers **load only at session start**
(so a fresh registration needs a restart) and often don't reconnect after a reclaim. If you still
want it, a committed repo-root `.mcp.json` makes it survive reclaim:

```json
{ "mcpServers": { "gitnexus": { "type": "stdio", "command": "node", "args": [".gitnexus/run.cjs", "mcp"] } } }
```

plus `.claude/settings.json` → `{ "enabledMcpjsonServers": ["gitnexus"] }`. Then restart the session.
`node .gitnexus/run.cjs setup` can write these for you. **But the default stance is: don't wait on
MCP — use the CLI.**

## 6. Command reference 📄

From `gitnexus --help` (v1.6.7):

| Command | Purpose |
|---|---|
| `analyze [path]` | Index a repository (full analysis) |
| `index [path...]` | Register an existing `.gitnexus/` into the global registry (no re-analysis) |
| `status` | Index status for current repo |
| `list` | List all indexed repos |
| `doctor` | Runtime platform capabilities + embedding config |
| `clean` / `remove <target>` | Delete index for current / named repo |
| `impact [target]` | Blast-radius analysis |
| `context [name]` | 360° view of a symbol |
| `query <search>` | Search knowledge graph for execution flows |
| `detect-changes` | Map git diff hunks to indexed symbols + flows |
| `cypher <query>` | Raw Cypher against the graph |
| `wiki [path]` | Generate repo wiki from the graph |
| `serve` | Local HTTP server for the web UI |
| `mcp` | Start MCP server (stdio) |
| `setup` / `uninstall` | Add/remove MCP entries + skills + hooks in detected editors |
| `group` | Manage repo groups for cross-index impact |

---

## 7. One-shot review recipe

```bash
node .gitnexus/run.cjs status || node .gitnexus/run.cjs analyze   # ensure the index is current
node .gitnexus/run.cjs impact <symbol-you-are-about-to-edit> --summary-only   # before editing
# … make the change, commit it …
node .gitnexus/run.cjs detect-changes -s compare -b <pre-change-commit>       # before pushing
```
