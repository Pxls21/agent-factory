#!/usr/bin/env python3
"""Export ONE Hermes session (a PC lane run) from the profile's state.db into a scrubbed markdown
transcript, so the lane's reasoning travels home with its patch (owner ask 2026-09-03: Hermes
pushes its transcript too, a curator model reads it all).

Reads sessions + messages (role, timestamp, content, tool_name / tool_calls names); tool RESULT
bodies are summarized by length only; every turn is capped; the same structural scrubber as
scripts/transcript_export.py is applied (imported by path so the two never drift).

Usage: hermes-session-export.py --db <state.db> --session <id> --out <file.md> [--cap 3000] [--tool-body-cap 0]
Exit 0 = written, 3 = session not found, 2 = usage.
"""
import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import re
import sqlite3
import sys

HERE = pathlib.Path(__file__).resolve()
SCRUB_SRC = HERE.parents[2] / "scripts" / "transcript_export.py"


def _scrub():
    spec = importlib.util.spec_from_file_location("transcript_export", SCRUB_SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.scrub


_HEADING_SHAPED = re.compile(r"(?m)^(## (?:user|assistant|tool result \())")


def _body(scrub, text: str, cap: int) -> str:
    """Cap, scrub, and indent any heading-shaped line by one space so the export grammar stays
    unambiguous: a quoted `## user @ …` inside a body would otherwise read as a turn boundary
    to the consumer (qwen_matrix.parse_export)."""
    return _HEADING_SHAPED.sub(r" \1", scrub(text[:cap]))


def export(db: str, session: str, out: str, cap: int, tool_body_cap: int = 0) -> bool:
    """tool_body_cap 0 (the default) keeps tool-result bodies OUT of the export — the committed
    transcripts stay body-less; > 0 exports them scrubbed and capped (matrix corpora on the PC)."""
    scrub = _scrub()
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    s = con.execute("select * from sessions where id=?", (session,)).fetchone()
    if s is None:
        return False
    keys = set(s.keys())
    started = dt.datetime.fromtimestamp(s["started_at"], dt.timezone.utc).isoformat() if "started_at" in keys and s["started_at"] else "?"
    lines = [f"# Hermes lane session {session}", "",
             f"- model: {s['model'] if 'model' in keys else '?'}",
             f"- started: {started}",
             f"- cwd: {s['cwd'] if 'cwd' in keys else '?'}",
             f"- messages: {s['message_count'] if 'message_count' in keys else '?'}; tool calls: {s['tool_call_count'] if 'tool_call_count' in keys else '?'}",
             f"- tokens in/out/cache_read/reasoning: {s['input_tokens'] if 'input_tokens' in keys else '?'}/{s['output_tokens'] if 'output_tokens' in keys else '?'}/{s['cache_read_tokens'] if 'cache_read_tokens' in keys else '?'}/{s['reasoning_tokens'] if 'reasoning_tokens' in keys else '?'}",
             ""]
    rows = con.execute("select role, timestamp, content, tool_name, tool_calls from messages where session_id=? order by id", (session,)).fetchall()
    for r in rows:
        ts = dt.datetime.fromtimestamp(r["timestamp"], dt.timezone.utc).strftime("%H:%M:%S") if r["timestamp"] else "?"
        role = r["role"]
        if role == "tool":
            head = f"## tool result ({r['tool_name'] or '?'}) @ {ts} — {len(r['content'] or '')} chars"
            if tool_body_cap > 0:
                lines.append(f"{head} (body capped at {tool_body_cap})\n\n{_body(scrub, r['content'] or '', tool_body_cap)}\n")
            else:
                lines.append(f"{head} (body not exported)\n")
            continue
        names = ""
        if r["tool_calls"]:
            try:
                calls = json.loads(r["tool_calls"])
                names = ", ".join((c.get("function") or {}).get("name") or c.get("name") or "?" for c in calls)
            except (json.JSONDecodeError, TypeError, AttributeError):
                names = "(unparsed)"
        body = _body(scrub, r["content"] or "", cap)
        lines.append(f"## {role} @ {ts}" + (f" → tools: {names}" if names else "") + f"\n\n{body}\n")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_text("\n".join(lines) + "\n")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=int, default=3000)
    ap.add_argument("--tool-body-cap", type=int, default=0,
                    help="export scrubbed tool-result bodies capped at N chars (default 0: not exported)")
    a = ap.parse_args()
    if not export(a.db, a.session, a.out, a.cap, a.tool_body_cap):
        print(f"hermes-session-export: session {a.session} not found in {a.db}", file=sys.stderr)
        return 3
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
