#!/usr/bin/env python3
"""WIKI-CONTEXT hook (owner directive 2026-08-25): on every user prompt,
lex-match the prompt against wiki page headings and inject the most relevant
excerpts, so the coordinator gets the system's own map without a manual
lookup — the wiki becomes the first-read continuity source.

Contract: UserPromptSubmit hook. Reads hook JSON on stdin, prints (headings +
bounded excerpts) to stdout, ALWAYS exits 0. Silent when nothing scores —
noise is worse than absence. The live-state page (wiki/topics/live-state.md)
is ALWAYS injected first when present: it is the turn-maintained continuity
snapshot that survives disk resets.
"""
import json
import re
import sys
from pathlib import Path

WIKI = Path(__file__).resolve().parents[2] / "wiki"
LIVE_STATE = WIKI / "topics" / "live-state.md"
MAX_PAGES = 3
EXCERPT_LINES = 12
STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "it",
    "that", "this", "with", "you", "we", "i", "me", "my", "our", "your", "do",
    "does", "can", "how", "what", "why", "just", "like", "yeah", "um", "uh",
    "also", "know", "now", "get", "go", "be", "have", "was", "are", "at",
}


# Harness events are not a person's prompt: task notifications, agent hand-backs and hook feedback arrive inside a
# conversation that already holds the context (compaction re-injects live-state through session-start.sh). Measured
# 2026-09-24 once the hooks fired in the /home/user session (task #214): 6.5 KB per plain prompt and 11.5 KB per
# notification, repeated on every background event.
HARNESS_EVENT_PREFIXES = ("[SYSTEM NOTIFICATION", "Another Claude session sent a message", "Stop hook feedback",
                          "<task-notification>", "<agent-message")
LIVE_BLOCK_MAX_LINES = 30
# The harness swaps any hook text over 10,000 characters for a 2 KB preview of its head (VERIFY-COORD-0924 F-L1-3, read
# from the running binary), and the incident log's entries are single lines of 2-3 KB, so every part is bounded in
# characters, not only in lines.
LIVE_BLOCK_MAX_CHARS = 4500
LINE_MAX_CHARS = 300
MATCH_MAX_CHARS = 1000
OUTPUT_MAX_CHARS = 8000


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9_]{3,}", text.lower()) if w not in STOPWORDS}


def live_block(lines: list[str]) -> list[str]:
    """The newest dated block under '## Active lanes' (the page's convention: newest first), else the first 40 lines."""
    try:
        start = lines.index("## Active lanes")
    except ValueError:
        return lines[:40]
    heads = [i for i in range(start + 1, len(lines)) if lines[i].startswith("**20")]
    if not heads:
        return lines[:40]
    end = heads[1] if len(heads) > 1 else len(lines)
    return lines[heads[0]:end][:LIVE_BLOCK_MAX_LINES]


def bounded(lines: list[str], limit: int, line_max: int) -> list[str]:
    """Whole lines up to `limit` characters in total; a line over `line_max` is cut and marked."""
    out: list[str] = []
    used = 0
    for line in lines:
        if len(line) > line_max:
            line = line[:line_max] + " [...]"
        if used + len(line) + 1 > limit:
            break
        out.append(line)
        used += len(line) + 1
    return out


def main() -> int:
    if sys.argv[1:] == ["--live-block"]:  # session-start.sh prints the same bounded block
        if LIVE_STATE.is_file():
            body = LIVE_STATE.read_text(errors="replace").strip().splitlines()
            print("\n".join(bounded(live_block(body), LIVE_BLOCK_MAX_CHARS, LIVE_BLOCK_MAX_CHARS)))
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    prompt = payload.get("prompt") or ""
    if not prompt.strip() or not WIKI.is_dir() or prompt.lstrip().startswith(HARNESS_EVENT_PREFIXES):
        return 0
    qtok = tokens(prompt)

    out: list[str] = []
    if LIVE_STATE.is_file():
        body = LIVE_STATE.read_text(errors="replace").strip().splitlines()
        out.append("[wiki live-state — the newest block; the page holds the rest]")
        out.extend(bounded(live_block(body), LIVE_BLOCK_MAX_CHARS, LIVE_BLOCK_MAX_CHARS))

    if qtok:
        # Incident integration (owner directive 2026-08-25): the anti-pattern
        # ledger and bug-echo reports search alongside the wiki, so bug-class
        # prompts pull registry rows without a manual lookup.
        repo = WIKI.parent
        extra = [repo / "docs" / "INCIDENT-LOG.md"]
        extra += sorted((repo / ".agents" / "research").glob("*bug-echo*.md"))
        candidates = [p for p in WIKI.rglob("*.md")] + [p for p in extra if p.is_file()]
        scored: list[tuple[float, Path, list[str]]] = []
        for page in candidates:
            if page == LIVE_STATE:
                continue
            try:
                text = page.read_text(errors="replace")
            except Exception:
                continue
            headings = [l for l in text.splitlines() if l.startswith("#")]
            score = len(qtok & tokens(" ".join(headings))) * 3 + len(
                qtok & tokens(page.stem.replace("-", " "))
            ) * 2
            if score > 0:
                score += len(qtok & tokens(text)) * 0.1
                scored.append((score, page, text.splitlines()))
        scored.sort(key=lambda t: -t[0])
        for score, page, lines in scored[:MAX_PAGES]:
            best_i, best_s = 0, -1.0
            for i, l in enumerate(lines):
                if l.startswith("#"):
                    s = len(qtok & tokens(" ".join(lines[i : i + EXCERPT_LINES])))
                    if s > best_s:
                        best_i, best_s = i, s
            try:
                label = f"wiki match: {page.relative_to(WIKI)}"
            except ValueError:
                label = f"incident match: {page.relative_to(WIKI.parent)}"
            out.append(f"[{label}]")
            out.extend(bounded(lines[best_i : best_i + EXCERPT_LINES], MATCH_MAX_CHARS, LINE_MAX_CHARS))

    if out:
        print("\n".join(bounded(out, OUTPUT_MAX_CHARS, LIVE_BLOCK_MAX_CHARS)))
        print("[wiki-context: excerpts are a MAP, not gospel — verify load-bearing claims against tree/ledger]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
