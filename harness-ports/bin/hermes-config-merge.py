#!/usr/bin/env python3
"""Merge harness-ports/hermes/config-snippet.yaml into a Hermes config.yaml — ADD-ONLY.

Owner ruling 2026-09-03: Hermes on the PC runs the build lanes with this repo's configuration
(skills dir, MCP servers, hooks, approvals). Hermes has no repo-scoped config, so the snippet
must be merged into the per-profile ~/.hermes/config.yaml. This script does that without ever
overwriting a key the owner already set:
  - scalars/dicts: added only where ABSENT (existing values win, recursively)
  - lists (external_dirs, deny, command_allowlist): UNION, order preserved, no duplicates
  - ${VAR} placeholders in the snippet are replaced by --set VAR=value (absolute paths; the
    merged file is per-machine anyway)
A timestamped backup is written next to the config before any write. Prints every key it
added and every key it left alone. Exit 0 = merged (or nothing to do), 2 = usage error.

Usage: hermes-config-merge.py --config ~/.hermes/config.yaml --snippet <snippet.yaml>
       --set AF_REPO=/abs/path --set AF_VENV=/abs/path --set CODEBASE_MEMORY_BIN=/abs/bin [--dry-run]
"""
import argparse
import datetime as _dt
import re
import shutil
import sys
from pathlib import Path

import yaml

ADDED, KEPT = [], []


def _subst(obj, env):
    if isinstance(obj, str):
        def rep(m):
            k = m.group(1)
            if k not in env:
                raise SystemExit(f"unresolved ${{{k}}} in snippet — pass --set {k}=...")
            return env[k]
        return re.sub(r"\$\{(?:env:)?([A-Za-z_][A-Za-z0-9_]*)\}", rep, obj)
    if isinstance(obj, list):
        return [_subst(x, env) for x in obj]
    if isinstance(obj, dict):
        return {k: _subst(v, env) for k, v in obj.items()}
    return obj


def _merge(dst, src, path=""):
    for k, v in src.items():
        p = f"{path}.{k}" if path else k
        if k not in dst:
            dst[k] = v
            ADDED.append(p)
        elif isinstance(dst[k], dict) and isinstance(v, dict):
            _merge(dst[k], v, p)
        elif isinstance(dst[k], list) and isinstance(v, list):
            before = len(dst[k])
            for item in v:
                if item not in dst[k]:
                    dst[k].append(item)
            (ADDED if len(dst[k]) > before else KEPT).append(f"{p} (list: +{len(dst[k]) - before})")
        else:
            KEPT.append(p)
    return dst


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--snippet", required=True)
    ap.add_argument("--set", action="append", default=[], metavar="VAR=value")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    env = {}
    for kv in a.set:
        if "=" not in kv:
            print(f"bad --set {kv}", file=sys.stderr)
            return 2
        k, v = kv.split("=", 1)
        env[k] = v
    cfg_path, snip_path = Path(a.config).expanduser(), Path(a.snippet).expanduser()
    cfg = yaml.safe_load(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg = cfg or {}
    snippet = yaml.safe_load(snip_path.read_text()) or {}
    snippet = _subst(snippet, env)
    merged = _merge(cfg, snippet)
    print("ADDED:"); [print("  +", p) for p in ADDED] or print("  (nothing)")
    print("KEPT (owner value wins):"); [print("  =", p) for p in KEPT] or print("  (nothing)")
    if a.dry_run:
        print("dry-run: config not written")
        return 0
    if ADDED:
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = cfg_path.with_name(cfg_path.name + f".bak-before-agent-factory-{stamp}")
        if cfg_path.exists():
            shutil.copy2(cfg_path, backup)
            print(f"backup: {backup}")
        cfg_path.write_text(yaml.safe_dump(merged, sort_keys=False, allow_unicode=True))
        print(f"written: {cfg_path}")
    else:
        print("nothing to add — config untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
