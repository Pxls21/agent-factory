#!/usr/bin/env python3
"""strip_cbm_hooks.py: remove the codebase-memory-mcp hooks from a Claude Code settings file (idempotent).

The codebase-memory-mcp installer writes seven hooks into ~/.claude/settings.json: `cbm-code-discovery-gate` before every
Grep and Glob and after every Read, and `cbm-session-reminder` / `cbm-subagent-reminder` at session and subagent start. The
S1A audit (docs/research/findings/system1-context/AUDIT-2026-09-25.md, D7) found none of them had injected anything since
2026-09-18, and the gate costs about 2.0 s per call with 0 bytes out (measured 2026-09-25: 2,032 / 2,009 / 2,008 ms), so
every Read, Grep and Glob paid two seconds for nothing. The codebase-memory MCP server and CLI stay; only these hooks go.

  strip_cbm_hooks.py [SETTINGS_JSON]      (default ~/.claude/settings.json)

Prints one line: how many hooks it removed (0 when there were none). Exit 0, or 2 when the file is not valid JSON (it is then
left untouched). A missing file is a no-op.
"""
import json
import os
import sys

MARK = "/.claude/hooks/cbm-"


def strip(settings):
    """-> (settings, removed): every hook whose command names a cbm- hook script is dropped; empty groups and events go."""
    removed = 0
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return settings, 0
    for event in list(hooks):
        groups = []
        for group in hooks[event] if isinstance(hooks[event], list) else []:
            kept = [h for h in group.get("hooks", []) if MARK not in str(h.get("command", ""))]
            removed += len(group.get("hooks", [])) - len(kept)
            if kept:
                groups.append(dict(group, hooks=kept))
        if groups:
            hooks[event] = groups
        else:
            del hooks[event]
    if not hooks:
        del settings["hooks"]
    return settings, removed


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    path = argv[0] if argv else os.path.expanduser("~/.claude/settings.json")
    if not os.path.exists(path):
        print("strip_cbm_hooks: %s absent; nothing to do" % path)
        return 0
    try:
        with open(path, encoding="utf-8") as fh:
            settings = json.load(fh)
    except ValueError:
        print("strip_cbm_hooks: %s is not valid JSON; left untouched" % path, file=sys.stderr)
        return 2
    settings, removed = strip(settings)
    if removed:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    print("strip_cbm_hooks: removed %d codebase-memory hook(s) from %s" % (removed, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
