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


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9_]{3,}", text.lower()) if w not in STOPWORDS}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    prompt = payload.get("prompt") or ""
    if not prompt.strip() or not WIKI.is_dir():
        return 0
    qtok = tokens(prompt)

    out: list[str] = []
    if LIVE_STATE.is_file():
        body = LIVE_STATE.read_text(errors="replace").strip().splitlines()
        out.append("[wiki live-state — turn-maintained continuity snapshot]")
        out.extend(body[:40])

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
            out.extend(lines[best_i : best_i + EXCERPT_LINES])

    if out:
        print("\n".join(out))
        print("[wiki-context: excerpts are a MAP, not gospel — verify load-bearing claims against tree/ledger]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
