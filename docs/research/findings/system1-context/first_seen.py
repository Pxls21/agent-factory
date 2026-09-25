#!/usr/bin/env python3
"""first_seen.py — S1A evidence demand 5, the ground truth: where five registry rows' symptoms first appear in the chat.

Each signature is a record SHAPE, not a free-text search, so a command that merely names the symptom does not count:
  AF-AP-154  an assistant refusal (message.stop_reason "refusal") after which the next real assistant record is served
             by another model than the last real one before it (the refusal record itself is model "<synthetic>")
  AF-AP-181  a tool_result block whose text holds "'gone' == 'Z'" (the race handler's fallback its own assert rejects)
  AF-AP-183  a hook_success attachment whose stdout is over 10,000 characters (the harness keeps a ~2 KB preview in
             `content`)
  AF-AP-201  a tool_result block whose text holds "EngineDeadError" (the shared vLLM server died)
  AF-AP-209  a tool_result block whose text holds "ERR_OUT_OF_RANGE" (a fractional timeout reached AbortSignal.timeout)
Prints, per signature: the count, the first 3 hits (timestamp, kind, project folder, file, line number, carrier, and
for AF-AP-183 the two lengths), and the hits per day. Positions and counts only; no transcript text.

Usage: first_seen.py [--root /root/.claude/projects] [--exclude BASENAME]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

def text_of(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False) if v is not None else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/root/.claude/projects")
    ap.add_argument("--exclude", action="append", default=[])
    a = ap.parse_args()
    root = Path(a.root)
    hits = collections.defaultdict(list)
    for f in sorted(root.rglob("*.jsonl")):
        if f.name in a.exclude or f.name == "journal.jsonl":
            continue
        rel = f.relative_to(root).parts
        kind = "main" if len(rel) == 2 else "subagent"
        where = (kind, rel[0], f.name)
        last_real = None
        pending = None
        with open(f, "rb") as fh:
            for i, line in enumerate(fh, 1):
                interesting = (b'"assistant"' in line or b"hook_success" in line or b"EngineDeadError" in line
                               or b"ERR_OUT_OF_RANGE" in line or b"'gone' == 'Z'" in line)
                if not interesting:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                ts = r.get("timestamp") or "?"
                t = r.get("type")
                msg = r.get("message") if isinstance(r.get("message"), dict) else {}
                if t == "assistant":
                    model = msg.get("model")
                    if msg.get("stop_reason") == "refusal":
                        pending = (ts, last_real, i)
                    elif model and model != "<synthetic>":
                        if pending and pending[1] and model != pending[1]:
                            hits["AF-AP-154"].append((pending[0], *where, pending[2], "refusal: %s -> %s" % (pending[1], model)))
                        pending = None
                        last_real = model
                if t == "user":
                    c = msg.get("content")
                    if isinstance(c, list):
                        for b in c:
                            if isinstance(b, dict) and b.get("type") == "tool_result":
                                txt = text_of(b.get("content"))
                                carrier = "tool_result:error" if b.get("is_error") else "tool_result"
                                if "EngineDeadError" in txt:
                                    hits["AF-AP-201"].append((ts, *where, i, carrier))
                                if "ERR_OUT_OF_RANGE" in txt:
                                    hits["AF-AP-209"].append((ts, *where, i, carrier))
                                if "'gone' == 'Z'" in txt:
                                    hits["AF-AP-181"].append((ts, *where, i, carrier))
                if t == "attachment" and isinstance(r.get("attachment"), dict):
                    att = r["attachment"]
                    if att.get("type") == "hook_success" and len(text_of(att.get("stdout"))) > 10000:
                        hits["AF-AP-183"].append((ts, *where, i, "hook_success:%s stdout=%d content=%d" % (
                            att.get("hookEvent"), len(text_of(att.get("stdout"))), len(text_of(att.get("content"))))))
    for sig in ("AF-AP-154", "AF-AP-181", "AF-AP-183", "AF-AP-201", "AF-AP-209"):
        h = sorted(hits[sig])
        print(f"## {sig}: {len(h)} hits")
        for x in h[:3]:
            print("  first:", " | ".join(str(v) for v in x))
        for kind in ("main", "subagent"):
            k = [x for x in h if x[1] == kind]
            if k:
                print(f"  first in a {kind} file:", " | ".join(str(v) for v in k[0]))
        days = collections.Counter(x[0][:10] for x in h)
        print("  per day:", ", ".join(f"{d} {n}" for d, n in sorted(days.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
