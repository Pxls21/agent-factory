#!/usr/bin/env python3
"""Build the committed synthetic S0-06 negative bundles.

This is a fixture generator, not proof evidence: it never starts or contacts ai-memory. The
producer shape mirrors `collect_leg.sh`'s 48 leaves so the checker can reject drift before any
semantic assertion runs.
"""
from __future__ import annotations

DOC = "Build the committed synthetic S0-06 negative bundles."

import argparse
import filecmp
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / "proofs" / "S0-06"
FIXTURES = PROOF / "fixtures"
ADAPTER = PROOF / "adapter" / "factory_memory.py"
SCOPE_ORDER = ("agent", "project", "team", "company")
TIMESTAMPS = {
    "agent": "2026-09-05T09:14:02Z",
    "project": "2026-09-04T17:41:55Z",
    "team": "2026-09-03T11:07:30Z",
    "company": "2026-09-01T08:22:11Z",
}
RANKS = {
    "collision": {"agent": -1.05, "project": -1.10, "team": -1.15, "company": -1.20},
    "only": {"agent": -0.72, "project": -0.77, "team": -0.82, "company": -0.87},
    "canary": {"agent": -0.92, "project": -0.97, "team": -1.02, "company": -1.07},
}


def _load_adapter():
    spec = importlib.util.spec_from_file_location("s0_06_fixture_factory_memory", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("factory_memory.py is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fm = _load_adapter()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True, allow_nan=False) + "\n" for row in rows))


def project_for(scope: str, agent: str) -> str:
    return {
        "agent": f"agent--{agent}",
        "project": "project--p-atlas",
        "team": "team--t-core",
        "company": "_global",
    }[scope]


def tuple_doc(agent: str) -> dict:
    return {"actor": "svc-agent-runner", "agent": agent, "project": "p-atlas", "team": "t-core"}


def snippet(body: str) -> str:
    return body.split("\n\n", 1)[1].strip()


def load_inputs() -> tuple[dict, dict]:
    return (
        json.loads((FIXTURES / "records-precedence.json").read_text(encoding="utf-8")),
        json.loads((FIXTURES / "honeytokens.json").read_text(encoding="utf-8")),
    )


def search_hits(agent: str, records: dict, tokens: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for scope in SCOPE_ORDER:
        project = project_for(scope, agent)
        variant = records["variants"][scope]
        only = records["scope_only"][scope]
        out[scope] = [
            {
                "kind": "decision",
                "path": records["stable_id"],
                "project": project,
                "rank": RANKS["collision"][scope],
                "snippet": snippet(variant["body"]),
                "title": variant["title"],
                "workspace": "factory",
            },
            {
                "kind": "decision",
                "path": only["path"],
                "project": project,
                "rank": RANKS["only"][scope],
                "snippet": snippet(only["body"]),
                "title": only["title"],
                "workspace": "factory",
            },
            {
                "kind": "decision",
                "path": records["honeytoken_path_template"].format(scope=scope),
                "project": project,
                "rank": RANKS["canary"][scope],
                "snippet": f"honeytoken {tokens[scope]} staged in the {scope} scope.",
                "title": f"Canary ({scope})",
                "workspace": "factory",
            },
        ]
    return out


def recall_doc(agent: str, allowed_scopes: list[str], records_by_scope: dict[str, list[dict]]) -> dict:
    by_scope = {
        scope: [fm.normalize_hit(hit, scope, TIMESTAMPS[scope]) for hit in records_by_scope[scope]]
        for scope in allowed_scopes
    }
    return {
        "binding": tuple_doc(agent),
        "degraded_scopes": [],
        "reason": "recall: complete",
        "records": fm.merge(by_scope),
        "scopes_queried": [
            {"project": project_for(scope, agent), "scope": scope, "workspace": "factory"}
            for scope in allowed_scopes
        ],
        "status": "ok",
    }


def query_event(query: str) -> dict:
    return {"path": "/api/v1/search",
            "query_sha256_16": hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]}


def page_event_path(scope: str, agent: str) -> str:
    return f"/api/v1/workspaces/factory/projects/{project_for(scope, agent)}/pages"


def recall_events(agent: str, scopes: list[str], query: str, record_count: int | None) -> list[dict]:
    seq = 1
    rows = [{
        "agent": agent,
        "authorized_scopes": scopes,
        "event": "scope_tuple_authorized",
        "reason": "authz: tuple matched the committed table",
        "seq": seq,
    }]
    seq += 1
    for scope in scopes:
        rows.append(dict(query_event(query), event="http_request", method="GET",
                         reason="substrate: request issued", seq=seq))
        seq += 1
        rows.append({"event": "http_request", "method": "GET", "path": page_event_path(scope, agent),
                     "reason": "substrate: request issued", "seq": seq})
        seq += 1
    done = {"degraded_scopes": [], "event": "recall_complete", "reason": "recall: complete", "seq": seq}
    if record_count is not None:
        done["record_count"] = record_count
    rows.append(done)
    return rows


def write_page_path(key: dict) -> str:
    return fm.idempotency_path(key["session"], key["turn"], key["event_id"])


def write_events(first: bool, page_path: str, key: dict) -> list[dict]:
    rows = [
        {"agent": "a-alpha", "authorized_scopes": list(SCOPE_ORDER), "event": "scope_tuple_authorized",
         "reason": "authz: tuple matched the committed table", "seq": 1},
        {"event": "write_intent", "key": key, "page_path": page_path, "project": "agent--a-alpha",
         "reason": "write: intent recorded", "scope": "agent", "seq": 2},
        {"event": "http_request", "method": "GET", "path": page_event_path("agent", "a-alpha"),
         "reason": "substrate: request issued", "seq": 3},
    ]
    if first:
        rows += [
            {"event": "http_request", "method": "POST", "path": "/admin/write-page",
             "reason": "substrate: request issued", "seq": 4},
            {"event": "write_committed", "key": key, "page_path": page_path,
             "project": "agent--a-alpha", "reason": "write: page written", "scope": "agent",
             "seq": 5},
        ]
    else:
        rows.append({"event": "write_noop", "key": key, "page_path": page_path,
                     "project": "agent--a-alpha", "reason": "write: idempotent no-op",
                     "scope": "agent", "seq": 4})
    return rows


def page_lists(agent: str, records: dict, tokens: dict, *, plant_project: bool) -> dict[str, list[dict]]:
    key = {"event_id": "evt-0003", "session": "sess-7f2a", "turn": "12"}
    page_path = write_page_path(key)
    out: dict[str, list[dict]] = {}
    for scope in SCOPE_ORDER:
        variant = records["variants"][scope]
        only = records["scope_only"][scope]
        rows = [
            {"kind": "decision", "path": records["stable_id"], "tier": "semantic",
             "title": variant["title"], "updated_at": TIMESTAMPS[scope]},
            {"kind": "decision", "path": only["path"], "tier": "semantic",
             "title": only["title"], "updated_at": TIMESTAMPS[scope]},
            {"kind": "decision", "path": records["honeytoken_path_template"].format(scope=scope),
             "tier": "semantic", "title": f"Canary ({scope})", "updated_at": TIMESTAMPS[scope]},
        ]
        if scope == "agent" or (plant_project and scope == "project"):
            rows.append({"kind": "fact", "path": page_path, "tier": "semantic",
                         "title": "Retention decision", "updated_at": "2026-09-05T09:30:00Z"})
        out[scope] = rows
    return out


def substrate() -> dict:
    return {
        "bin_path": "/tmp/s0-06-run/src/ai-memory/target/release/ai-memory",
        "binary_sha256_observed": "5c1d0b7a4e93f26810ab3d5c47e9f0128d6b4a35c9e70f21db83a6c4517e9b0d",
        "cargo_version": "cargo 1.95.0 (a1b2c3d4e 2025-11-04)",
        "commit": "73715b6f1b2f0abb0a8b0ed47c1f69b1bd1b806e",
        "component": "ai-memory",
        "data_dir": "/tmp/s0-06-run/data",
        "origin": "http://127.0.0.1:8765",
        "port": 8765,
        "posture": {
            "AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL": "true",
            "AI_MEMORY_AUTO_IMPROVE__SCHEDULER__ENABLED": "false",
            "AI_MEMORY_MAINTENANCE__ENABLED": "false",
            "AI_MEMORY_SLOTS__PER_USER": "false",
        },
        "posture_observed": {
            "AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL": "true",
            "AI_MEMORY_AUTO_IMPROVE__SCHEDULER__ENABLED": "false",
            "AI_MEMORY_MAINTENANCE__ENABLED": "false",
            "AI_MEMORY_SLOTS__PER_USER": "false",
        },
        "rustc_version": "rustc 1.95.0 (f5e6d7c8b 2025-10-28)",
        "version": "1.39.0",
        "version_command": "ai-memory --version",
        "version_stdout": "ai-memory 1.39.0",
    }


PROVENANCE_PREFIX = """# PROVENANCE — committed NEGATIVE evidence bundle

This bundle is a complete 48-leaf S0-06 evidence root that would PASS `check_four_scope.py` except for ONE
planted defect (named at the bottom). It is a hostile input for the checker, never proof evidence:
nothing here was produced by a running ai-memory, and the `substrate.json` values marked SYNTHETIC
below are invented. A real leg is captured by `proofs/S0-06/tools/pc/collect_leg.sh` on the PC.

## Producer-shape instrument

The committed bytes are generated by `proofs/S0-06/fixtures/build_synthetic_bundles.py` from the
collector's declared shape: root `substrate.json` + `PROVENANCE.md`, denied 4 leaves, precedence 15
leaves, write-scope 15 leaves, and leak 13 leaves. The loopback collector-shape exercise in
VERIFY-M2 measured the same 48-leaf shape without running ai-memory; that was a SHAPE instrument
only, not substrate evidence.

## Record shapes — VERBATIM from the pinned ai-memory source (commit 73715b6f)

| file | shape | source |
|---|---|---|
| `precedence/raw-<scope>.json`, `leak/raw-<scope>.json` | `GET /api/v1/search` response: a JSON array of `ApiSearchHit` = exactly `{workspace, project, path, title, kind, snippet, rank}` | `crates/ai-memory-web/src/routes/api.rs:1254-1263`; the array is built by `enrich_hits` `:1009-1030`; the route is `:41-45` and the scoped branch `scoped_search_mode` `:352-360` |
| `write-scope/raw-<scope>.json` | `GET /api/v1/workspaces/{ws}/projects/{p}/pages` response: a JSON array of `PageSummary` = exactly `{path, title, kind, tier, updated_at}` | `crates/ai-memory-store/src/reader.rs:1174-1185`; the route is `crates/ai-memory-web/src/routes/api.rs:33-36`, handler `pages_handler` `:157-171` |
| `precedence/recall-*.json`, `leak/recall.json`, `denied/recall.json` | the adapter's own result document | produced by calling `proofs/S0-06/adapter/factory_memory.py`'s `normalize_hit` + `merge` on the raw hits above, so the fixture cannot drift from the producer (AF-AP-42) |
| `write-scope/write.json`, `retry.json` | the adapter's write result; `page_path` is `idempotency_path("sess-7f2a", "12", "evt-0003")` computed by the adapter | `factory_memory.py` `idempotency_path` |
| `denied/events.jsonl`, `precedence/events-*.jsonl`, `write-scope/events-*.jsonl`, `leak/events.jsonl` | adapter decision events as emitted by `FactoryMemory._emit`, with search events carrying route-only `path=/api/v1/search` plus `query_sha256_16=<16hex>` | `factory_memory.py` `_emit` / `_search`; the query text is not in the telemetry path |
| `write-scope/record.json` | the exact write request body that produced `write.json`; checker re-derives path/key/type from it | `collect_leg.sh` `record.json` heredoc and `factory_memory.py` `write` |
| `leak/honeytokens.json` | the staged tokens, one per scope | `proofs/S0-06/fixtures/honeytokens.json` |
| `substrate.json` `commit` / `version` / `origin` | `73715b6f1b2f0abb0a8b0ed47c1f69b1bd1b806e` / `1.39.0` / `http://127.0.0.1:8765` | `upstream.lock.yaml:33-38`; origin is the run's non-secret scheme/host/port recorded by `start_ai_memory.sh` |
| `<leg>/tuple.json` | the caller-supplied identity tuple the runner writes into each leg — `{actor, agent, team, project}`, no `scopes` field | written by `collect_leg.sh`'s `tuple_file()`; the ids come from `proofs/S0-06/adapter/bindings.json` |
| `<leg>/raw-<scope>.url` | the URL that raw read was actually fetched from, recorded by curl itself (`-w '%{url_effective}'`) | `collect_leg.sh` `raw_search`/`raw_pages`/`raw_leak_search` |
| `<leg>/substrate-observed.json` | that leg's own re-hash of the serving binary — `{bin_path, binary_sha256_observed, leg}` | `collect_leg.sh`; the checker requires all five reads of the digest to agree (provenance, not a pin) |
| `denied/socket-witness.json`, `precedence/socket-witness.json` | the instance port's socket 4-tuples before and after the leg — `{after, before, instrument, port}` | `collect_leg.sh` `socket_snapshot()`/`write_witness()`; the substrate-side instrument for assertion 1, with the precedence leg as its paired positive control |
| `substrate.json` `posture_observed` | the four posture variables READ BACK from the serving child's `/proc/<pid>/environ` | `start_ai_memory.sh`; only those four keys are read — a prefix match would also copy `AI_MEMORY_AUTH_TOKEN` into the bundle |
| `substrate.json` `posture` | the four safe-posture variables and their required values | `docs/04_MEMORY_AND_GOVERNANCE.md` §6 and `.env.example:37-43`; the `__` nesting is real — `figment.merge(Env::prefixed("AI_MEMORY_").split("__"))`, `crates/ai-memory-cli/src/config.rs:937` |

## SYNTHETIC values (invented for this fixture, not read off any instance)

- `substrate.json`: `binary_sha256_observed`, `bin_path`, `cargo_version`, `rustc_version`,
  `version_stdout`, `origin`, `port`, `data_dir` (`version_stdout` is the shape clap prints for
  `#[command(name = "ai-memory", version)]`, `crates/ai-memory-cli/src/cli.rs:11`).
- `denied/socket-witness.json` and `precedence/socket-witness.json`: every 4-tuple. The denied
  leg's `after` equals its `before` (no connection was opened); the precedence leg's `after` adds
  20 client sockets and drops two that expired from TIME-WAIT, which is why the checker grades the
  SET difference rather than a count delta.
- `<leg>/raw-<scope>.url`: the URLs a run against `127.0.0.1:8765` would have produced.
- `<leg>/substrate-observed.json`: `bin_path` and the digest, matching `substrate.json`.
- Every `rank` (a plausible negative FTS5 score), every `updated_at` / `timestamp`, every
  `page_id`, every page title and body text, and the honeytoken hex suffixes.
- The scope ids behind the project names (`a-alpha`, `a-beta`, `t-core`, `p-atlas`) come from the
  committed authorization table `proofs/S0-06/adapter/bindings.json`.
"""


def write_substrate_observed(root: Path, substrate_doc: dict) -> None:
    for leg in ("denied", "precedence", "write-scope", "leak"):
        dump(root / leg / "substrate-observed.json", {
            "bin_path": substrate_doc["bin_path"],
            "binary_sha256_observed": substrate_doc["binary_sha256_observed"],
            "leg": leg,
        })


def write_denied(root: Path, substrate_doc: dict) -> None:
    dump(root / "denied" / "recall.json", {
        "degraded_scopes": [],
        "reason": "denied: scope-tuple-unauthorized",
        "records": [],
        "scopes_queried": [],
        "status": "denied",
    })
    write_jsonl(root / "denied" / "events.jsonl", [{
        "event": "scope_tuple_denied",
        "presented_fields": ["actor", "agent", "project", "team"],
        "reason": "denied: scope-tuple-unauthorized",
        "seq": 1,
    }])
    dump(root / "denied" / "socket-witness.json", {
        "after": ["127.0.0.1:8765 0.0.0.0:*", "127.0.0.1:41002 127.0.0.1:8765",
                  "127.0.0.1:41004 127.0.0.1:8765", "127.0.0.1:41006 127.0.0.1:8765"],
        "before": ["127.0.0.1:8765 0.0.0.0:*", "127.0.0.1:41002 127.0.0.1:8765",
                   "127.0.0.1:41004 127.0.0.1:8765", "127.0.0.1:41006 127.0.0.1:8765"],
        "instrument": "ss -Htan ( sport = :8765 or dport = :8765 )",
        "port": substrate_doc["port"],
    })


def write_precedence(root: Path, records: dict, tokens: dict) -> None:
    alpha_hits = search_hits("a-alpha", records, tokens)
    dump(root / "precedence" / "tuple.json", tuple_doc("a-alpha"))
    for scope in SCOPE_ORDER:
        dump(root / "precedence" / f"raw-{scope}.json", alpha_hits[scope][:2])
        (root / "precedence" / f"raw-{scope}.url").write_text(
            f"http://127.0.0.1:8765/api/v1/search?q=deploy+window&workspace=factory"
            f"&project={project_for(scope, 'a-alpha')}&limit=20\n")
    precedence = recall_doc("a-alpha", list(SCOPE_ORDER), {s: alpha_hits[s][:2] for s in SCOPE_ORDER})
    dump(root / "precedence" / "recall-1.json", precedence)
    dump(root / "precedence" / "recall-2.json", precedence)
    write_jsonl(root / "precedence" / "events-1.jsonl",
                recall_events("a-alpha", list(SCOPE_ORDER), "deploy window", len(precedence["records"])))
    write_jsonl(root / "precedence" / "events-2.jsonl",
                recall_events("a-alpha", list(SCOPE_ORDER), "deploy window", len(precedence["records"])))
    dump(root / "precedence" / "socket-witness.json", {
        "after": ["127.0.0.1:41002 127.0.0.1:8765", "127.0.0.1:41006 127.0.0.1:8765"]
                 + [f"127.0.0.1:{port} 127.0.0.1:8765" for port in range(41100, 41140, 2)]
                 + ["127.0.0.1:8765 0.0.0.0:*"],
        "before": ["127.0.0.1:41002 127.0.0.1:8765", "127.0.0.1:41006 127.0.0.1:8765",
                   "127.0.0.1:8765 0.0.0.0:*"],
        "instrument": "ss -Htan ( sport = :8765 or dport = :8765 )",
        "port": 8765,
    })


def write_write_scope(root: Path, records: dict, tokens: dict, *, planted: str) -> None:
    key = {"event_id": "evt-0003", "session": "sess-7f2a", "turn": "12"}
    page_path = write_page_path(key)
    dump(root / "write-scope" / "tuple.json", tuple_doc("a-alpha"))
    dump(root / "write-scope" / "record.json", {
        "body": "# Retention decision\n\nStage-0 observation written by the authorized active scope.\n",
        "event_id": "evt-0003",
        "session": "sess-7f2a",
        "turn": "12",
    })
    dump(root / "write-scope" / "write.json", {
        "idempotency_key": key,
        "page_id": "3f8d1c66-9a2e-4b70-8d51-0c7a4e12b9f3",
        "page_path": page_path,
        "project": "agent--a-alpha",
        "reason": "write: page written",
        "scope": "agent",
        "status": "ok",
        "workspace": "factory",
    })
    dump(root / "write-scope" / "retry.json", {
        "idempotency_key": key,
        "page_id": None,
        "page_path": page_path,
        "project": "agent--a-alpha",
        "reason": "write: idempotent no-op",
        "scope": "agent",
        "status": "ok",
        "workspace": "factory",
    })
    for scope, rows in page_lists("a-alpha", records, tokens, plant_project=(planted == "wrong-scope")).items():
        dump(root / "write-scope" / f"raw-{scope}.json", rows)
        (root / "write-scope" / f"raw-{scope}.url").write_text(
            f"http://127.0.0.1:8765/api/v1/workspaces/factory/projects/{project_for(scope, 'a-alpha')}/pages\n")
    write_jsonl(root / "write-scope" / "events-write.jsonl", write_events(True, page_path, key))
    write_jsonl(root / "write-scope" / "events-retry.jsonl", write_events(False, page_path, key))


def write_leak(root: Path, records: dict, tokens: dict, *, planted: str) -> None:
    beta_hits = search_hits("a-beta", records, tokens)
    dump(root / "leak" / "tuple.json", tuple_doc("a-beta"))
    dump(root / "leak" / "honeytokens.json", tokens)
    for scope in SCOPE_ORDER:
        canary = [hit for hit in beta_hits[scope] if hit["path"].startswith("canaries/")]
        dump(root / "leak" / f"raw-{scope}.json", canary)
        (root / "leak" / f"raw-{scope}.url").write_text(
            f"http://127.0.0.1:8765/api/v1/search?q=honeytoken&workspace=factory"
            f"&project={project_for(scope, 'a-beta')}&limit=20\n")
    leak = recall_doc("a-beta", ["agent", "project"],
                      {scope: [hit for hit in beta_hits[scope] if hit["path"].startswith("canaries/")]
                       for scope in SCOPE_ORDER})
    if planted == "leak":
        team_hit = [hit for hit in beta_hits["team"] if hit["path"] == "canaries/team.md"][0]
        leak["records"].append(fm.normalize_hit(team_hit, "team", TIMESTAMPS["team"]))
    dump(root / "leak" / "recall.json", leak)
    write_jsonl(root / "leak" / "events.jsonl", recall_events("a-beta", ["agent", "project"], "honeytoken", None))


def write_provenance(root: Path, planted: str) -> None:
    if planted == "wrong-scope":
        (root / "PROVENANCE.md").write_text(PROVENANCE_PREFIX + """
## The planted defect

`write-scope/raw-project.json` carries the written observation's page path as well, so the record
the adapter reported writing into `agent--a-alpha` is also present in `project--p-atlas`. Every
other file is the passing bundle. Expected verdict:

    write: record found in project   (exit 1)
""")
    elif planted == "leak":
        (root / "PROVENANCE.md").write_text(PROVENANCE_PREFIX + """
## The planted defect

`leak/recall.json` carries one extra merged record whose snippet contains `HT-team-c52e6f04` — the
honeytoken staged in `team--t-core`, surfacing in a recall for a binding authorized for Agent and
Project only. Every other file is the passing bundle. Expected verdict:

    leak: honeytoken HT-team-c52e6f04 surfaced from team   (exit 1)
""")
    else:
        raise ValueError(planted)


def build_bundle(root: Path, planted: str) -> None:
    records, tokens = load_inputs()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    substrate_doc = substrate()
    dump(root / "substrate.json", substrate_doc)
    write_denied(root, substrate_doc)
    write_precedence(root, records, tokens)
    write_write_scope(root, records, tokens, planted=planted)
    write_leak(root, records, tokens, planted=planted)
    write_substrate_observed(root, substrate_doc)
    write_provenance(root, planted)


def build_all(out: Path) -> None:
    build_bundle(out / "evidence-wrong-scope-write", "wrong-scope")
    build_bundle(out / "evidence-leak", "leak")


def compare_dirs(want: Path, got: Path) -> list[str]:
    mismatches: list[str] = []
    for rel in ("evidence-wrong-scope-write", "evidence-leak"):
        want_files = {p.relative_to(want / rel).as_posix() for p in (want / rel).rglob("*") if p.is_file()}
        got_files = {p.relative_to(got / rel).as_posix() for p in (got / rel).rglob("*") if p.is_file()}
        for name in sorted(want_files ^ got_files):
            mismatches.append(f"{rel}/{name}: missing on one side")
        for name in sorted(want_files & got_files):
            if not filecmp.cmp(want / rel / name, got / rel / name, shallow=False):
                mismatches.append(f"{rel}/{name}: bytes differ")
    return mismatches


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=DOC)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=FIXTURES)
    args = parser.parse_args(argv)
    if args.check:
        with tempfile.TemporaryDirectory(prefix="s0-06-fixtures-") as tmp:
            built = Path(tmp)
            build_all(built)
            mismatches = compare_dirs(FIXTURES, built)
        if mismatches:
            print("synthetic S0-06 fixtures differ from the generator:", file=sys.stderr)
            for item in mismatches:
                print(item, file=sys.stderr)
            return 1
        print("synthetic S0-06 fixtures match the generator")
        return 0
    build_all(args.out)
    print(f"synthetic S0-06 fixtures written under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
