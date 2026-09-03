#!/usr/bin/env python3
"""Bounded session-transcript reader for the read-the-chat-first recovery rule
(session-continuity skill, owner mandate 2026-08-28).

Prints (a) an events-per-hour histogram for a given day — a TIME HOLE across a
window that origin's commits span means the work ran in a SIBLING session —
and (b) the last N real user turns (tool_results and list-shaped payloads
skipped), each truncated, so a confused resume can re-ground without loading
the whole multi-hundred-MB JSONL.

For SEMANTIC questions ("what did the owner decide about X"), use --export:
it writes one clean markdown file per day (user + assistant text, hook/
notification noise stripped) and the reader — a person or an agent Read —
is the semantic engine. Do NOT point graft at chat history: measured
2026-08-28, `graft build` parsed 0 of 0 files on a 3.8MB markdown chat
corpus (its parsers are language grammars; prose has no wiring) and `ask`
returned empty. Graft answers CODE questions; this script + Read answers
chat-history questions.

Usage:
  python scripts/chat_tail.py <transcript.jsonl> [--turns N] [--day YYYY-MM-DD]
  python scripts/chat_tail.py <transcript.jsonl> --export <dir>   # daily corpus
"""
import argparse
import json
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--turns", type=int, default=12)
    ap.add_argument("--day", default=None, help="YYYY-MM-DD for the histogram")
    ap.add_argument("--export", default=None, metavar="DIR",
                    help="write one markdown file per day (user+assistant text, noise stripped) for semantic Read")
    args = ap.parse_args()

    if args.export:
        os.makedirs(args.export, exist_ok=True)
        files: dict[str, object] = {}
        n = 0
        with open(args.path) as f:
            for line in f:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                t = e.get("type")
                if t not in ("user", "assistant"):
                    continue
                c = e.get("message", {}).get("content")
                if isinstance(c, str):
                    txt = c
                elif isinstance(c, list):
                    txt = "\n".join(
                        b.get("text", "")
                        for b in c
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                else:
                    continue
                txt = txt.strip()
                if not txt or txt.startswith("[{"):
                    continue
                if t == "user" and txt.startswith(
                    ("Stop hook feedback:", "<task-notification>", "<system-reminder>")
                ):
                    continue
                ts = e.get("timestamp", "?")
                day = ts[:10] if ts != "?" else "undated"
                fh = files.get(day)
                if fh is None:
                    fh = files[day] = open(
                        os.path.join(args.export, f"chat-{day}.md"), "w"
                    )
                    fh.write(f"# Conversation {day}\n\n")
                fh.write(f"## {t} @ {ts}\n\n{txt[:4000]}\n\n")
                n += 1
        for fh in files.values():
            fh.close()
        print(f"exported {n} turns into {len(files)} daily files under {args.export}")
        return 0

    users: list[tuple[str, str]] = []
    hours: dict[str, int] = {}
    probe = f'"timestamp":"{args.day}T' if args.day else None
    with open(args.path) as f:
        for line in f:
            if probe:
                i = line.find(probe)
                if i >= 0:
                    h = line[i + len(probe): i + len(probe) + 2]
                    hours[h] = hours.get(h, 0) + 1
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") != "user":
                continue
            c = e.get("message", {}).get("content")
            if isinstance(c, str):
                txt = c
            elif isinstance(c, list):
                txt = " ".join(
                    b.get("text", "")
                    for b in c
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            else:
                continue
            txt = txt.strip()
            if not txt or txt.startswith("[{"):
                continue
            if txt.startswith(
                ("Stop hook feedback:", "<task-notification>", "<system-reminder>")
            ):
                continue
            users.append((e.get("timestamp", "?"), txt))

    if probe:
        print(f"events/hour on {args.day}: {sorted(hours.items())}")
        print("(a zero-event window that origin commits span = sibling-session hole)")
    for ts, txt in users[-args.turns:]:
        print("=" * 20, ts)
        print(txt.replace("\n", " ")[:600])
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
