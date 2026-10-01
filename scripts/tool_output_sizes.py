#!/usr/bin/env python3
"""Measure the sizes of tool outputs in Claude Code transcripts (counts only).

The question it answers (owner, 2026-10-01): how large are the outputs the model
reads, so that the Jev pruner's floor sits at a realistic level instead of the
upstream's 10,000 tokens. It streams each transcript line by line, pairs every
tool_use with its tool_result, and prints a size distribution per tool. It
never prints the text of an output.

Sizes are the characters of the inline tool_result the model received and an
estimate of its tokens by the pruner's own estimator (jev-pruner
src/jev.ts estimateTokens: a word one token per six letters, a digit half a
token, any other symbol nine tenths). A result the harness saved to a file
("<persisted-output>") is counted apart, at the size its header states: the
model saw only its preview, so the distribution covers the inline results.

Usage: tool_output_sizes.py [--since YYYY-MM-DD] [--json OUT] TRANSCRIPT...
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

# The plugin's regex is /[A-Za-z]+|\d+|[^\sA-Za-z\d]/g in JavaScript, where \d is ASCII only and \s is this set.
_JS_SPACE = "".join(chr(code) for code in (
    0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0xA0, 0x1680, *range(0x2000, 0x200B),
    0x2028, 0x2029, 0x202F, 0x205F, 0x3000, 0xFEFF))
TOKEN_PIECES = re.compile("[A-Za-z]+|[0-9]+|[^" + re.escape(_JS_SPACE) + "A-Za-z0-9]")
PERSISTED = re.compile(r"Output too large \(([0-9.]+)(B|KB|MB)\)")
UNIT = {"B": 1, "KB": 1024, "MB": 1024 * 1024}
BUCKETS = [250, 500, 1000, 2000, 3000, 5000, 7500, 10000, 20000]


def estimate_tokens(text: str) -> int:
    tokens = 0.0
    for match in TOKEN_PIECES.finditer(text):
        piece = match.group(0)
        first = piece[0]
        if "0" <= first <= "9":
            tokens += len(piece) / 2
        elif "A" <= first <= "Z" or "a" <= first <= "z":
            tokens += 1 + (len(piece) - 1) // 6
        else:
            tokens += 0.9
            if ord(first) > 0xFFFF:  # JavaScript walks UTF-16 code units: an astral symbol is two pieces
                tokens += 0.9
    return math.ceil(tokens)


def result_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            part.get("text", "") for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return ""


def scan(paths: list[Path], since: str | None) -> dict:
    names: dict[str, str] = {}
    rows: dict[str, list[dict]] = {}
    for path in paths:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if '"tool_use"' not in line and '"tool_result"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                stamp = record.get("timestamp") or ""
                if since and stamp[:10] < since:
                    continue
                message = record.get("message")
                if not isinstance(message, dict):
                    continue
                content = message.get("content")
                if not isinstance(content, list):
                    continue
                for part in content:
                    if not isinstance(part, dict):
                        continue
                    if part.get("type") == "tool_use":
                        names[part.get("id", "")] = part.get("name", "?")
                    elif part.get("type") == "tool_result":
                        name = names.get(part.get("tool_use_id", ""), "?")
                        text = result_text(part.get("content"))
                        hit = PERSISTED.search(text[:400]) if text.startswith("<persisted-output>") else None
                        if hit:
                            chars = int(float(hit.group(1)) * UNIT[hit.group(2)])
                            rows.setdefault(name, []).append({"chars": chars, "tokens": None, "persisted": True})
                        else:
                            rows.setdefault(name, []).append(
                                {"chars": len(text), "tokens": estimate_tokens(text), "persisted": False})
    return rows


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    index = min(len(sorted_values) - 1, max(0, math.ceil(q * len(sorted_values)) - 1))
    return sorted_values[index]


def summarize(rows: dict[str, list[dict]]) -> dict:
    out = {}
    for name, items in sorted(rows.items(), key=lambda kv: -len(kv[1])):
        inline = [r for r in items if not r["persisted"]]
        if not inline:
            continue
        ratio = sum(r["tokens"] for r in inline) / max(1, sum(r["chars"] for r in inline))
        tokens = sorted(r["tokens"] for r in inline)
        chars = sorted(r["chars"] for r in inline)
        persisted = sorted(r["chars"] for r in items if r["persisted"])
        buckets = {}
        for edge in BUCKETS:
            buckets[f">{edge}"] = sum(1 for t in tokens if t > edge)
        out[name] = {
            "results": len(items),
            "inline": len(inline),
            "persisted": len(persisted),
            "persisted_chars_p50": percentile(persisted, 0.50),
            "tokens_per_char_inline": round(ratio, 4),
            "tokens_mean": round(sum(tokens) / len(tokens), 1),
            "tokens_p50": percentile(tokens, 0.50),
            "tokens_p75": percentile(tokens, 0.75),
            "tokens_p90": percentile(tokens, 0.90),
            "tokens_p95": percentile(tokens, 0.95),
            "tokens_p99": percentile(tokens, 0.99),
            "tokens_max": tokens[-1],
            "chars_p50": percentile(chars, 0.50),
            "chars_p90": percentile(chars, 0.90),
            "chars_max_inline": chars[-1],
            "tokens_total": sum(tokens),
            "tokens_above": {k: v for k, v in buckets.items()},
            "token_share_above": {
                f">{edge}": round(sum(t for t in tokens if t > edge) / max(1, sum(tokens)), 3) for edge in BUCKETS
            },
        }
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", help="only results stamped on or after this UTC day (YYYY-MM-DD)")
    parser.add_argument("--json", help="write the summary as JSON to this path")
    parser.add_argument("--tools", default="Bash,Read,Grep,Glob", help="tools to print (comma list; 'all' for every tool)")
    parser.add_argument("transcripts", nargs="+")
    args = parser.parse_args(argv)
    paths = [Path(p) for p in args.transcripts]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        print(f"tool_output_sizes: no such file: {missing[0]}", file=sys.stderr)
        return 64
    summary = summarize(scan(paths, args.since))
    if args.json:
        Path(args.json).write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    wanted = None if args.tools == "all" else set(args.tools.split(","))
    for name, row in summary.items():
        if wanted is not None and name not in wanted:
            continue
        print(f"{name}: results {row['results']} inline {row['inline']} persisted {row['persisted']} "
              f"(source p50 {row['persisted_chars_p50']} chars); inline: mean {row['tokens_mean']} "
              f"p50 {row['tokens_p50']} p75 {row['tokens_p75']} p90 {row['tokens_p90']} p95 {row['tokens_p95']} "
              f"p99 {row['tokens_p99']} max {row['tokens_max']} (tokens; inline max {row['chars_max_inline']} chars)")
        print("  inline results above: " + " ".join(f"{k} {v}" for k, v in row["tokens_above"].items()))
        print("  inline token share above: " + " ".join(f"{k} {v}" for k, v in row["token_share_above"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
