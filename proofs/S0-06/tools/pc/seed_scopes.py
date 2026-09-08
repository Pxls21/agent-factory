#!/usr/bin/env python3
"""S0-06 PC leg — stage the four scopes through ai-memory's RAW write surface. NOT run in the sandbox.

Deliberately independent of `proofs/S0-06/adapter/factory_memory.py`: the adapter is the subject
of the proof, so the seeding instrument must not share its code. Everything here goes straight to
`POST /admin/write-page` (`crates/ai-memory-mcp/src/admin.rs:636`, body `WritePageAdminRequest`
`:6332-6358`) — the same route ai-memory's own `ai-memory write-page` CLI posts to
(`crates/ai-memory-cli/src/commands/write_page.rs:1-5`). `/api/v1` is read-only (docs/02:73).

What it stages, from the committed inputs `proofs/S0-06/fixtures/records-precedence.json` and
`proofs/S0-06/fixtures/honeytokens.json`:

  * the SAME `stable_id` in all four scopes with a different body per scope (so an agent-first
    merge is a real precedence result, not the only record there was);
  * one scope-only page per scope (so the four raw reads are not identical sets);
  * one honeytoken page per scope.

Scope -> (workspace, project) is docs/03 §4 with workspace `factory`. NOTE: Company is written as
the ordinary project `factory/_global`, NOT ai-memory's reserved global scope — that one is
`(default, _global)` by construction (`lookup_global_scope`,
`crates/ai-memory-store/src/scope.rs:254-271`, and `create_global_scope` `:277-292`). Writing it
explicitly is what keeps Company inside the `factory` workspace the plan pins.

    seed_scopes.py --base-url URL --token-file F --agent A --team T --project P
"""
from __future__ import annotations

import argparse
import json
import stat
import sys
import urllib.request
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
SCOPES = ("agent", "project", "team", "company")


def read_json(path: Path):
    if not stat.S_ISREG(Path(path).lstat().st_mode):
        raise ValueError(f"not a regular file: {path}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def projects_for(agent: str, team: str, project: str) -> dict:
    return {
        "agent": f"agent--{agent}",
        "project": f"project--{project}",
        "team": f"team--{team}",
        "company": "_global",
    }


def write_page(base_url: str, token: str, project: str, path: str, title: str, body: str) -> dict:
    payload = {
        "workspace": "factory",
        "project": project,
        "path": path,
        "title": title,
        "body": body,
        "kind": "decision",
        "tier": "semantic",
        "tags": ["s0-06"],
        "pinned": False,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/admin/write-page",
        data=json.dumps(payload, sort_keys=True).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + token},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--agent", required=True)
    ap.add_argument("--team", required=True)
    ap.add_argument("--project", required=True)
    args = ap.parse_args(argv)

    token_path = Path(args.token_file)
    if not stat.S_ISREG(token_path.lstat().st_mode):
        raise ValueError(f"not a regular file: {token_path}")
    token = token_path.read_text(encoding="utf-8").strip()   # value never printed

    records = read_json(FIXTURES / "records-precedence.json")
    tokens = read_json(FIXTURES / "honeytokens.json")
    projects = projects_for(args.agent, args.team, args.project)

    staged = []
    for scope in SCOPES:
        project = projects[scope]
        variant = records["variants"][scope]
        write_page(args.base_url, token, project, records["stable_id"],
                   variant["title"], variant["body"])
        staged.append((scope, project, records["stable_id"]))
        only = records["scope_only"][scope]
        write_page(args.base_url, token, project, only["path"], only["title"], only["body"])
        staged.append((scope, project, only["path"]))
        canary_path = records["honeytoken_path_template"].format(scope=scope)
        canary_body = records["honeytoken_body_template"].format(scope=scope, token=tokens[scope])
        write_page(args.base_url, token, project, canary_path, f"Canary ({scope})", canary_body)
        staged.append((scope, project, canary_path))

    for scope, project, path in staged:
        print(f"seeded {scope} {project} {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
