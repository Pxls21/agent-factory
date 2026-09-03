"""Replay Edit/Write tool calls from builder transcript JSONL onto the tree.
Chronological across the given transcripts; only for the named target files."""
import json, sys, os

TARGETS = {p for p in os.environ.get("REPLAY_TARGETS", "").split(",") if p}  # REPLAY_TARGETS=/abs/a.py,/abs/b.py
assert TARGETS, "set REPLAY_TARGETS (comma-separated absolute paths) before replaying"
calls = []  # (ts, kind, input)
for path in sys.argv[1:]:
    for line in open(path, errors="replace"):
        try:
            e = json.loads(line)
        except Exception:
            continue
        # tool_use entries live in assistant messages' content arrays
        msg = e.get("message") or {}
        for c in (msg.get("content") or []):
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in ("Edit", "Write"):
                inp = c.get("input") or {}
                fp = inp.get("file_path")
                if fp in TARGETS:
                    ts = e.get("timestamp") or ""
                    if ts >= "2026-08-27T00:00":
                        calls.append((ts, c["name"], inp))
calls.sort(key=lambda x: x[0])
print(f"replaying {len(calls)} calls")
applied = failed = 0
for ts, kind, inp in calls:
    fp = inp["file_path"]
    if kind == "Write":
        open(fp, "w").write(inp["content"]); applied += 1
        print(f"W {ts[11:19]} {os.path.basename(fp)}")
        continue
    old, new = inp["old_string"], inp["new_string"]
    src = open(fp).read()
    n = src.count(old)
    if n == 0:
        # may already be applied (idempotent) or genuinely missing
        if new in src:
            print(f"= {ts[11:19]} {os.path.basename(fp)} (already applied)")
            applied += 1
        else:
            print(f"X {ts[11:19]} {os.path.basename(fp)} OLD NOT FOUND")
            failed += 1
        continue
    if inp.get("replace_all"):
        src = src.replace(old, new)
    else:
        src = src.replace(old, new, 1)
    open(fp, "w").write(src); applied += 1
    print(f"E {ts[11:19]} {os.path.basename(fp)}")
print(f"done: {applied} applied, {failed} FAILED")
