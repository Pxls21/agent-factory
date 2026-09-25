#!/usr/bin/env python3
"""Where the re-sent context comes from, by kind of content (counts only).

Every API request re-sends the whole context. A piece of content that enters the conversation stays until the next
compaction, so its cost is its size times the requests that follow it (the P1 seed's residency formula,
scripts/jev_pipes/accounting.tokens_saved: characters / 4.06 x following requests). This walks each transcript once and
sums that cost per kind: tool results by tool, tool inputs by tool (a Write's content, a Bash command), assistant text,
thinking, and user-side text (typed messages, system reminders and hook context arrive as user-record text). The segment
base (what each request after a compaction starts with: the system prompt, tools, instructions and the summary) is the
first request's context times the requests in its segment.

  context_budget.py TRANSCRIPT.jsonl [...]

Prints sums and shares only; no transcript text leaves the process.
"""
import bisect
import collections
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from jev_pipes import accounting, transcript  # noqa: E402


def walk(path: str, cost: collections.Counter) -> tuple[int, int]:
    limit = os.path.getsize(path)
    index = transcript.scan(path, limit, set(), 10 ** 12, lambda s: frozenset())
    offs = index.request_offsets
    edges = [0] + index.boundaries + [limit]
    base = total = 0
    for a, b in zip(edges, edges[1:]):
        seg = index.requests[bisect.bisect_left(offs, a):bisect.bisect_left(offs, b)]
        if seg:
            base += seg[0].context_tokens * len(seg)
            total += sum(r.context_tokens for r in seg)
    calls = {}
    stats = collections.Counter()
    for offset, record in transcript.iter_records(path, limit, stats):
        kind = record.get("type")
        if kind not in ("assistant", "user"):
            continue
        following, _ = index.following(offset)
        if following == 0:
            continue
        for block in transcript._blocks(record):
            t = block.get("type")
            if kind == "assistant" and t == "tool_use":
                calls[block.get("id")] = block.get("name") or "?"
                size = len(json.dumps(block.get("input"), ensure_ascii=False))
                cost["tool input: " + (block.get("name") or "?")] += accounting.tokens_saved(size, following)
            elif kind == "assistant" and t == "text":
                cost["assistant text"] += accounting.tokens_saved(len(block.get("text") or ""), following)
            elif kind == "assistant" and t == "thinking":
                cost["assistant thinking (if kept)"] += accounting.tokens_saved(len(block.get("thinking") or ""), following)
            elif kind == "user" and t == "tool_result":
                name = calls.get(block.get("tool_use_id"), "?")
                cost["tool result: " + name] += accounting.tokens_saved(len(transcript.result_text(block)), following)
            elif kind == "user" and t == "text":
                cost["user-side text (messages, reminders, hook context)"] += accounting.tokens_saved(len(block.get("text") or ""), following)
    return base, total


def main(argv=None) -> int:
    paths = (argv if argv is not None else sys.argv[1:])
    cost = collections.Counter()
    base = total = 0
    for p in paths:
        b, t = walk(p, cost)
        base += b
        total += t
    growth = total - base
    attributed = sum(cost.values())
    print("re-sent %d tokens | segment base %d (%.1f%%) | in-segment growth %d (%.1f%%)" % (
        total, base, 100.0 * base / total, growth, 100.0 * growth / total))
    print("attributed by kind (chars/4.06 x following requests): %d tokens (%.1f%% of the growth)" % (
        attributed, 100.0 * attributed / growth if growth else 0))
    rows = sorted(cost.items(), key=lambda kv: -kv[1])
    other = sum(v for _, v in rows[15:])
    for k, v in rows[:15]:
        print("  %-58s %14.0f  %5.1f%% of re-sent" % (k, v, 100.0 * v / total))
    if other:
        print("  %-58s %14.0f  %5.1f%% of re-sent" % ("(the rest)", other, 100.0 * other / total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
