#!/usr/bin/env python3
"""Export a Claude Code session transcript into daily, SECRET-SCRUBBED markdown digests under
transcripts/sandbox/ (committed), so PC lanes and cheap curator models can read the chat history
the wiki/skills should be curated from (owner ask 2026-09-03: "a hook that every time you push it
sends a bit of the transcript to the repo").

Digest = user + assistant text only (tool results, hook noise and notifications stripped, same
rule as scripts/chat_tail.py --export), each turn capped, one file per UTC day, rewritten in
full each run (idempotent). Scrubbing is STRUCTURAL and tested: every class in SECRET_PATTERNS is
replaced before a byte reaches disk, and tests/test_transcript_export.py plants one of each and
asserts none survives. Never widen what is exported without extending the scrubber test.

Usage: transcript_export.py [--transcript <jsonl>] [--out transcripts/sandbox] [--cap 4000]
Default transcript: the newest *.jsonl under /root/.claude/projects/-home-user/.
Exit 0 = wrote/refreshed files (prints them), 3 = no transcript found.
"""
import argparse
import glob
import json
import os
import re
import sys

SECRET_PATTERNS = [
    # explicit credential assignments / headers (value part replaced)
    (re.compile(r"((?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|api[_-]?key|token|secret|password|passwd|Authorization)\s*[:=]\s*[\"']?)([^\s\"'&,;]{8,})", re.I), r"\1<redacted>"),
    (re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]{8,}"), r"\1<redacted>"),
    # provider-shaped keys
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b"), "sk-<redacted>"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"), "gh<redacted>"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b"), "AIza<redacted>"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}\b"), "xox-<redacted>"),
    # ephemeral bridge links (the token often rides in the URL's session)
    (re.compile(r"https?://[a-z0-9\-]+\.trycloudflare\.com[^\s)\"']*", re.I), "https://<bridge-link-redacted>"),
    # long opaque tokens (32+ url-safe chars) — coarse, deliberately
    (re.compile(r"\b[A-Za-z0-9_\-]{40,}\b"), "<opaque-redacted>"),
]


def scrub(text: str) -> str:
    for pat, rep in SECRET_PATTERNS:
        text = pat.sub(rep, text)
    return text


def turns(path):
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = e.get("type")
            if t not in ("user", "assistant"):
                continue
            c = (e.get("message") or {}).get("content")
            if isinstance(c, str):
                txt = c
            elif isinstance(c, list):
                txt = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
            else:
                continue
            txt = txt.strip()
            if not txt or txt.startswith("[{"):
                continue
            if t == "user" and txt.startswith(("Stop hook feedback:", "<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION")):
                continue
            yield t, e.get("timestamp", "?"), txt


def export(transcript: str, out: str, cap: int) -> list:
    os.makedirs(out, exist_ok=True)
    days = {}
    for role, ts, txt in turns(transcript):
        day = ts[:10] if ts != "?" else "undated"
        days.setdefault(day, []).append(f"## {role} @ {ts}\n\n{scrub(txt[:cap])}\n")
    written = []
    for day in sorted(days):
        p = os.path.join(out, f"chat-{day}.md")
        body = f"# Conversation {day} (scrubbed digest, {len(days[day])} turns)\n\n" + "\n".join(days[day])
        with open(p, "w") as fh:
            fh.write(body)
        written.append(p)
    return written


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript")
    ap.add_argument("--out", default="transcripts/sandbox")
    ap.add_argument("--cap", type=int, default=4000)
    a = ap.parse_args()
    path = a.transcript
    if not path:
        cands = sorted(glob.glob("/root/.claude/projects/-home-user/*.jsonl"), key=os.path.getmtime)
        path = cands[-1] if cands else None
    if not path or not os.path.isfile(path):
        print("transcript_export: no transcript found", file=sys.stderr)
        return 3
    for p in export(path, a.out, a.cap):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
