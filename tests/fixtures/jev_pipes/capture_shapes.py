#!/usr/bin/env python3
"""Capture the REAL transcript record shapes the P1 replay reads (key names and value type names only, never values).

    python3 tests/fixtures/jev_pipes/capture_shapes.py <main-session transcript.jsonl> > tests/fixtures/jev_pipes/record_shapes.json

The synthetic fixture (make_fixture.py) is held to these shapes by tests/test_jev_pipes_replay.py (AF-AP-42: a fixture
builder is pinned to a committed real producer sample). For each record kind the most common key set is kept.
"""
import collections
import json
import sys


def shape(value):
    if isinstance(value, dict):
        return {k: type(v).__name__ for k, v in sorted(value.items())}
    return type(value).__name__


def kind_of(record):
    t = record.get("type")
    content = (record.get("message") or {}).get("content") if isinstance(record.get("message"), dict) else None
    if t == "system":
        return "system:" + str(record.get("subtype"))
    if t == "user":
        if record.get("isCompactSummary"):
            return "user:compact_summary"
        if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return "user:tool_result"
        return "user:meta" if record.get("isMeta") else "user:prompt"
    return str(t)


def main(path):
    tops, messages, blocks, usages, results = (collections.defaultdict(collections.Counter) for _ in range(5))
    tools = {}
    with open(path, "rb") as handle:
        for raw in handle:
            try:
                record = json.loads(raw)
            except ValueError:
                continue
            kind = kind_of(record)
            if kind not in ("assistant", "user:tool_result", "user:prompt", "user:compact_summary", "system:compact_boundary"):
                continue
            tops[kind][json.dumps(shape(record), sort_keys=True)] += 1
            message = record.get("message")
            if isinstance(message, dict):
                messages[kind][json.dumps(shape(message), sort_keys=True)] += 1
                if isinstance(message.get("usage"), dict):
                    usages[kind][json.dumps(sorted(k for k in message["usage"] if k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")))] += 1
                for block in message.get("content") if isinstance(message.get("content"), list) else []:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_use":
                            tools[block.get("id")] = block.get("name")
                        blocks[f"{kind}/{block.get('type')}"][json.dumps(shape(block), sort_keys=True)] += 1
                        if block.get("type") == "tool_result" and tools.get(block.get("tool_use_id")) == "Bash" and isinstance(record.get("toolUseResult"), dict):
                            results["Bash"][json.dumps(shape(record["toolUseResult"]), sort_keys=True)] += 1
    top = lambda counter: {k: json.loads(v.most_common(1)[0][0]) for k, v in sorted(counter.items())}
    print(json.dumps({"source": "most common key sets per record kind; names and type names only",
                      "record": top(tops), "message": top(messages), "block": top(blocks),
                      "usage_keys": top(usages), "bash_tool_use_result": top(results)}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1])
