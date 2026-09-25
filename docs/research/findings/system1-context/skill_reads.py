#!/usr/bin/env python3
"""skill_reads.py — skills reached by a path other than the Skill tool: a Read of a file under a skills folder, and a Bash
command that names a SKILL.md. Counts per kind (main, subagent) and per skill name; no transcript text.

Patterns: Read `file_path` matching `/(?:\\.claude|\\.agents)/(?:lane-)?skills/<name>/` ; Bash `command` containing
`skills/<name>/SKILL.md` (a cat, sed, head, grep or an edit of it: a MENTION, not proof of reading).

Usage: skill_reads.py [--root /root/.claude/projects] [--exclude BASENAME]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

READ_RX = re.compile(r"/(?:\.claude|\.agents)/(?:lane-)?skills/([^/]+)/")
BASH_RX = re.compile(r"skills/([A-Za-z0-9_.-]+)/SKILL\.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/root/.claude/projects")
    ap.add_argument("--exclude", action="append", default=[])
    a = ap.parse_args()
    reads = collections.defaultdict(collections.Counter)
    bash = collections.defaultdict(collections.Counter)
    for f in sorted(Path(a.root).rglob("*.jsonl")):
        if f.name in a.exclude or f.name == "journal.jsonl":
            continue
        kind = "main" if len(f.relative_to(a.root).parts) == 2 else "subagent"
        with open(f, "rb") as fh:
            for line in fh:
                if b"skills/" not in line or b"tool_use" not in line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                m = r.get("message") if isinstance(r.get("message"), dict) else {}
                for b in m.get("content") or []:
                    if not isinstance(b, dict) or b.get("type") != "tool_use":
                        continue
                    inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                    if b.get("name") == "Read":
                        mm = READ_RX.search(str(inp.get("file_path") or ""))
                        if mm:
                            reads[kind][mm.group(1)] += 1
                    elif b.get("name") == "Bash":
                        for name in set(BASH_RX.findall(str(inp.get("command") or ""))):
                            bash[kind][name] += 1
    for kind in ("main", "subagent"):
        r, b = reads[kind], bash[kind]
        print(f"{kind}: Read calls under a skills folder {sum(r.values())} ({len(r)} skills): "
              + ", ".join(f"{k} {v}" for k, v in r.most_common()))
        print(f"{kind}: Bash commands naming a SKILL.md {sum(b.values())} ({len(b)} skills): "
              + ", ".join(f"{k} {v}" for k, v in b.most_common(25)) + (" ..." if len(b) > 25 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
