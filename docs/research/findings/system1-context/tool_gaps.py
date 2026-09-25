#!/usr/bin/env python3
"""tool_gaps.py — the wall time between a tool call and its result, per tool and period, from record timestamps.

For every assistant `tool_use` block it finds the user record whose `tool_result` carries the same id, and takes the
difference of the two records' `timestamp` fields. Silent hooks leave no record of their own (the harness writes a
hook record only when the hook prints), so this gap is the only trace a silent PreToolUse/PostToolUse run can leave.
Prints counts and milliseconds only.

Usage: tool_gaps.py --split 2026-09-18T19:43:00Z [--root /root/.claude/projects] [--exclude BASENAME] [--only TEXT]
"""
import argparse
import collections
import datetime as dt
import json
import statistics
import sys
from pathlib import Path


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/root/.claude/projects")
    ap.add_argument("--split", required=True)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--only", default="")
    ap.add_argument("--tools", default="Read,Edit,Write,Grep,Glob,Bash")
    a = ap.parse_args()
    split = ts(a.split)
    tools = a.tools.split(",")
    gaps = collections.defaultdict(list)  # (kind, period, tool) -> ms
    for f in sorted(Path(a.root).rglob("*.jsonl")):
        if f.name in a.exclude or a.only not in str(f) or f.name == "journal.jsonl":
            continue
        kind = "main" if len(f.relative_to(a.root).parts) == 2 else "subagent"
        pending = {}
        with open(f, "rb") as fh:
            for line in fh:
                if b"tool_use" not in line and b"tool_result" not in line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                m = r.get("message") if isinstance(r.get("message"), dict) else {}
                c = m.get("content")
                if not isinstance(c, list) or not isinstance(r.get("timestamp"), str):
                    continue
                for b in c:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use" and b.get("name") in tools:
                        pending[b.get("id")] = (b.get("name"), ts(r["timestamp"]))
                    elif b.get("type") == "tool_result" and b.get("tool_use_id") in pending:
                        name, t0 = pending.pop(b["tool_use_id"])
                        t1 = ts(r["timestamp"])
                        period = "before" if t0 < split else "after"
                        gaps[(kind, period, name)].append((t1 - t0).total_seconds() * 1000)
    print(f"split at {a.split}; gap = tool_result record timestamp minus tool_use record timestamp")
    print("| kind | period | tool | n | median ms | p25 ms | p75 ms | share >= 2000 ms |")
    print("|---|---|---|---|---|---|---|---|")
    for (kind, period, name), v in sorted(gaps.items()):
        q = statistics.quantiles(v, n=4) if len(v) >= 4 else [min(v), statistics.median(v), max(v)]
        share = sum(1 for x in v if x >= 2000) / len(v)
        print(f"| {kind} | {period} | {name} | {len(v)} | {statistics.median(v):.0f} | {q[0]:.0f} | {q[2]:.0f} | {share:.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
