# PROVENANCE — committed NEGATIVE evidence bundle

This bundle is a complete S0-06 evidence root that would PASS `check_four_scope.py` except for ONE
planted defect (named at the bottom). It is a hostile input for the checker, never proof evidence:
nothing here was produced by a running ai-memory, and the `substrate.json` values marked SYNTHETIC
below are invented. A real leg is captured by `proofs/S0-06/tools/pc/collect_leg.sh` on the PC.

## Record shapes — VERBATIM from the pinned ai-memory source (commit 73715b6f)

| file | shape | source |
|---|---|---|
| `precedence/raw-<scope>.json`, `leak/raw-<scope>.json` | `GET /api/v1/search` response: a JSON array of `ApiSearchHit` = exactly `{workspace, project, path, title, kind, snippet, rank}` | `crates/ai-memory-web/src/routes/api.rs:1254-1263`; the array is built by `enrich_hits` `:1009-1030`; the route is `:41-45` and the scoped branch `scoped_search_mode` `:352-360` |
| `write-scope/raw-<scope>.json` | `GET /api/v1/workspaces/{ws}/projects/{p}/pages` response: a JSON array of `PageSummary` = exactly `{path, title, kind, tier, updated_at}` | `crates/ai-memory-store/src/reader.rs:1174-1185`; the route is `crates/ai-memory-web/src/routes/api.rs:33-36`, handler `pages_handler` `:157-171` |
| `precedence/recall-*.json`, `leak/recall.json`, `denied/recall.json` | the adapter's own result document | produced by calling `proofs/S0-06/adapter/factory_memory.py`'s `normalize_hit` + `merge` on the raw hits above, so the fixture cannot drift from the producer (AF-AP-42) |
| `write-scope/write.json`, `retry.json` | the adapter's write result; `page_path` is `idempotency_path("sess-7f2a", "12", "evt-0003")` computed by the adapter | `factory_memory.py` `idempotency_path` |
| `denied/events.jsonl` | one adapter decision event per line, as emitted by `FactoryMemory._emit` | `factory_memory.py` `_emit` |
| `leak/honeytokens.json` | the staged tokens, one per scope | `proofs/S0-06/fixtures/honeytokens.json` |
| `substrate.json` `commit` / `version` | `73715b6f1b2f0abb0a8b0ed47c1f69b1bd1b806e` / `1.39.0` | `upstream.lock.yaml:33-38`; the version is `version = "1.39.0"` in the pinned `Cargo.toml:20` |
| `substrate.json` `posture` | the four safe-posture variables and their required values | `docs/04_MEMORY_AND_GOVERNANCE.md` §6 and `.env.example:37-43`; the `__` nesting is real — `figment.merge(Env::prefixed("AI_MEMORY_").split("__"))`, `crates/ai-memory-cli/src/config.rs:937` |

## SYNTHETIC values (invented for this fixture, not read off any instance)

- `substrate.json`: `binary_sha256`, `port`, `data_dir`.
- Every `rank` (a plausible negative FTS5 score), every `updated_at` / `timestamp`, every
  `page_id`, every page title and body text, and the honeytoken hex suffixes.
- The scope ids behind the project names (`a-alpha`, `a-beta`, `t-core`, `p-atlas`) come from the
  committed authorization table `proofs/S0-06/adapter/bindings.json`.

## The planted defect

`leak/recall.json` carries one extra merged record whose snippet contains `HT-team-c52e6f04` — the
honeytoken staged in `team--t-core`, surfacing in a recall for a binding authorized for Agent and
Project only. Every other file is the passing bundle. Expected verdict:

    leak: honeytoken HT-team-c52e6f04 surfaced from team   (exit 1)
