#!/usr/bin/env python3
"""footer_check.py — does the fast-jev-output function hook engage? Each tool_result that carries its footer
("[fast-jev-output ") is classified by the tool call that produced it: a call whose input names the plugin, jev-pruner
or scripts/jev_pipes QUOTES the footer (a test run, a cat, a grep); any other Bash call may be a real trim; a Read cannot
be trimmed by a Bash hook. Counts per kind, tool and class, and per day. No transcript text.

Usage: footer_check.py [--root /root/.claude/projects] [--exclude BASENAME]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

NAMES = ("fast-jev-output", "jev-pruner", "jev_pipes")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/root/.claude/projects")
    ap.add_argument("--exclude", action="append", default=[])
    a = ap.parse_args()
    res, days = collections.Counter(), collections.Counter()
    for f in sorted(Path(a.root).rglob("*.jsonl")):
        if f.name in a.exclude or f.name == "journal.jsonl":
            continue
        kind = "main" if len(f.relative_to(a.root).parts) == 2 else "subagent"
        calls = {}
        with open(f, "rb") as fh:
            for line in fh:
                if b"tool_use" not in line and b"fast-jev-output" not in line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                c = (r.get("message") or {}).get("content") if isinstance(r.get("message"), dict) else None
                if not isinstance(c, list):
                    continue
                for b in c:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use":
                        calls[b.get("id")] = (b.get("name"), json.dumps(b.get("input")))
                    elif b.get("type") == "tool_result":
                        t = b.get("content")
                        t = t if isinstance(t, str) else json.dumps(t)
                        if "[fast-jev-output " in t:
                            name, inp = calls.get(b.get("tool_use_id"), ("?", ""))
                            cls = "the call names the plugin (quoting)" if any(n in inp for n in NAMES) else "the call does not name it"
                            res[(kind, name, cls)] += 1
                            days[(kind, (r.get("timestamp") or "")[:10])] += 1
    for (kind, name, cls), v in sorted(res.items()):
        print(f"{kind} | {name} | {cls} | {v}")
    print("per day:", ", ".join(f"{k} {d} {v}" for (k, d), v in sorted(days.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
