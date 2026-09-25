#!/usr/bin/env python3
"""How much a model-free "present" step would save: tool results that repeat an earlier one exactly (counts only).

Within one compaction segment the model still holds every earlier tool result in its context, so a result whose text is
byte-identical to the last result of the same call (the same normalized Bash command, or the same tool input for Read, Grep
and Glob) could be shown as a one-line pointer ("same as the result at <time>") instead. After a compaction the earlier text
is gone, so the key memory resets there. The saving uses the P1 seed's formula (scripts/jev_pipes/accounting.tokens_saved):
characters saved / 4.06 x the requests until the next compaction, with a pointer of STUB_CHARS characters left in place.

  repeat_probe.py [--min-chars N] [--json OUT] TRANSCRIPT.jsonl [...]

Prints counts and sums only; no transcript text leaves the process. Reuses scripts/jev_pipes/transcript.py for the record
walk, the request index and the compaction boundaries (the P1 replay's own accounting).
"""
import argparse
import collections
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[4] / "scripts"))
from jev_pipes import accounting, transcript  # noqa: E402

STUB_CHARS = 120   # the pointer left in place of a repeated result
TOOLS = ("Bash", "Read", "Grep", "Glob")


def probe(path: str, min_chars: int) -> dict:
    limit = os.path.getsize(path)
    index = transcript.scan(path, limit, set(), 10 ** 12, lambda s: frozenset())   # requests and boundaries only
    boundaries = index.boundaries
    stats = collections.Counter()
    calls: dict[str, tuple[str, object]] = {}
    last: dict[tuple, str] = {}
    last_text: dict[tuple, str] = {}
    segment = 0
    by_tool = collections.defaultdict(lambda: collections.Counter())
    for offset, record in transcript.iter_records(path, limit, stats):
        while segment < len(boundaries) and offset >= boundaries[segment]:
            segment += 1
            last.clear()                      # a compaction: the earlier results are out of the model's context
            last_text.clear()
        kind = record.get("type")
        if kind == "assistant":
            for block in transcript._blocks(record):
                if block.get("type") == "tool_use":
                    calls[block.get("id")] = (block.get("name") or "?", block.get("input"))
            continue
        if kind != "user":
            continue
        for block in transcript._blocks(record):
            if block.get("type") != "tool_result":
                continue
            name, tool_input = calls.get(block.get("tool_use_id"), ("?", None))
            if name not in TOOLS:
                continue
            text = transcript.result_text(block)
            key = transcript.rerun_key(name, tool_input)
            digest = hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()
            c = by_tool[name]
            c["results"] += 1
            c["chars"] += len(text)
            following, _ = index.following(offset)
            c["residency_tokens"] += accounting.tokens_saved(len(text), following)   # the ceiling: every char re-sent
            prev = last_text.get(key)
            if len(text) >= min_chars and last.get(key) == digest:
                saved = len(text) - STUB_CHARS
                c["repeats"] += 1
                c["repeat_chars"] += len(text)
                c["tokens_saved"] += accounting.tokens_saved(saved, following)
            elif len(text) >= min_chars and prev is not None:
                # a re-run with a changed output: the lines it shares with the previous output (a multiset), which a
                # "same as last run except" presentation would leave out
                before = collections.Counter(prev.splitlines())
                shared = sum(len(line) + 1 for line in text.splitlines() if before[line] > 0 and not before.subtract([line]))
                c["reruns_changed"] += 1
                c["rerun_shared_chars"] += shared
                c["rerun_tokens_saved"] += accounting.tokens_saved(max(0, shared - STUB_CHARS), following)
            last[key] = digest
            last_text[key] = text
    resent = sum(r.context_tokens for r in index.requests)
    return {"path": path, "requests": len(index.requests), "compactions": len(boundaries), "context_tokens_resent": resent,
            "by_tool": {k: dict(v) for k, v in sorted(by_tool.items())}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("transcripts", nargs="+")
    ap.add_argument("--min-chars", type=int, default=500)
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    rows = [probe(p, args.min_chars) for p in args.transcripts]
    total = collections.Counter()
    resent = 0
    for r in rows:
        resent += r["context_tokens_resent"]
        for tool, c in r["by_tool"].items():
            for k, v in c.items():
                total[(tool, k)] += v
    print("transcripts %d | requests %d | context tokens re-sent %d | min_chars %d | pointer %d chars" % (
        len(rows), sum(r["requests"] for r in rows), resent, args.min_chars, STUB_CHARS))
    saved_all = 0.0
    resid_all = [0.0]
    for tool in TOOLS:
        n, ch = total[(tool, "results")], total[(tool, "chars")]
        rp, rc, ts = total[(tool, "repeats")], total[(tool, "repeat_chars")], total[(tool, "tokens_saved")]
        saved_all += ts
        print("%-5s results %7d chars %11d | exact repeats %6d chars %10d | tokens saved %14.0f" % (tool, n, ch, rp, rc, ts))
        print("      residency tokens %14.0f | changed re-runs %6d shared chars %11d | tokens saved %14.0f" % (
            total[(tool, "residency_tokens")], total[(tool, "reruns_changed")], total[(tool, "rerun_shared_chars")],
            total[(tool, "rerun_tokens_saved")]))
        saved_all += total[(tool, "rerun_tokens_saved")]
        resid_all[0] += total[(tool, "residency_tokens")]
    print("all   tool-output residency %.0f = %.2f%% of the context tokens re-sent" % (resid_all[0], 100.0 * resid_all[0] / resent if resent else 0))
    print("all   tokens saved (exact repeats + shared lines of re-runs) %.0f = %.2f%% of the context tokens re-sent" % (
        saved_all, 100.0 * saved_all / resent if resent else 0))
    if args.json:
        Path(args.json).write_text(json.dumps({"rows": rows, "min_chars": args.min_chars, "stub_chars": STUB_CHARS}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
