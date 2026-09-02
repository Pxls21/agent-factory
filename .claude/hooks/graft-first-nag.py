#!/usr/bin/env python3
"""PreToolUse nag for the GRAFT-FIRST owner mandate (2026-08-27, third telling).

Fires on Grep calls that look like SEMANTIC identifier searches over project
code (a single bare identifier pattern aimed at .py files) — the exact shape
the coordinator kept regressing to. Warns, never blocks: literal-token sweeps
(env var names, quoted strings, JSONL greps, regex with anchors/operators)
stay legal and mostly won't match the identifier shape.
"""
import json
import re
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("tool_name") != "Grep":
        return 0
    ti = payload.get("tool_input") or {}
    pattern = ti.get("pattern") or ""
    path = ti.get("path") or ""
    glob = ti.get("glob") or ""
    ftype = ti.get("type") or ""

    targets_py = (
        ftype == "py"
        or glob.endswith(".py")
        or "src" in path
        or (not path and not glob and not ftype)
    )
    # Bare identifier(s) — no regex operators beyond | between plain names.
    looks_semantic = bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*(\|[A-Za-z_][A-Za-z0-9_.]*)*", pattern))
    if targets_py and looks_semantic:
        print(
            "GRAFT-FIRST (owner mandate, CLAUDE.md code-intel section): this Grep is a "
            f"semantic identifier search ({pattern!r}). Use `graft ask \"<question>\"` "
            "(--source / --in <path>) instead — grep stays legal only for literal-token "
            "sweeps (exact strings, env names, logs, non-code files)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
