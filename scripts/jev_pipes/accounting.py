"""The P1 accounting (task #231; the brief's DESIGN 3 and the seed's bar), deterministic and LLM-free.

- Tokens saved = dropped characters / 4.06 (audit A's fitted characters per token) x the API requests that followed the
  result until the next compaction.
- A miss = a pruned result whose dropped text holds a distinctive token (a path, a number of 3+ digits, an identifier of
  6+ characters, hex of 7+) that appears in the session's next 20 tool inputs or assistant texts and nowhere in the kept
  text or the earlier history; or a re-run of the same command within the next 20 tool calls.
- A miss costs one request's whole context (the usage record of the next request). Net = saved minus miss costs.
- The bar: misses at or under 5% of pruned results AND net above zero (finite). Nothing pruned is a FAIL (net 0).
"""
from __future__ import annotations

import math
import re

CHARS_PER_TOKEN = 4.06
LOOKAHEAD = 20
MISS_RATE_BAR = 0.05

_PATH = re.compile(r"[A-Za-z0-9_.~@+-]*(?:/[A-Za-z0-9_.~@+-]+)+/?")
_NUMBER = re.compile(r"\b\d{3,}\b")
_IDENTIFIER = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{5,}\b")
_HEX = re.compile(r"\b[0-9a-fA-F]{7,}\b")


def tokens(text: str) -> frozenset:
    """The distinctive tokens of `text`; each class is matched on its own, so a path also yields its parts."""
    found = {m.group(0).rstrip(".,:;") for m in _PATH.finditer(text)}
    found.discard("")
    found.update(m.group(0) for m in _NUMBER.finditer(text))
    found.update(m.group(0) for m in _IDENTIFIER.finditer(text))
    found.update(m.group(0) for m in _HEX.finditer(text))
    return frozenset(found)


def miss(original: str, kept: str, history: set | frozenset, lookahead_tokens: list[frozenset],
         lookahead_calls: list[tuple | None], rerun_key: tuple) -> tuple[int, bool]:
    """(count of dropped distinctive tokens the next items used, whether the command re-ran within the lookahead)."""
    removed = tokens(original) - tokens(kept) - history
    used = set().union(*lookahead_tokens) if lookahead_tokens else set()
    return len(removed & used), rerun_key in lookahead_calls


def tokens_saved(chars_saved: int, following_calls: int) -> float:
    return chars_saved / CHARS_PER_TOKEN * following_calls


def percentile(values: list[float], q: float) -> float | None:
    """Nearest-rank percentile (q in 0..100); None for no values."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(q / 100 * len(ordered)))
    return ordered[rank - 1]


def verdict(rows: list[dict]) -> dict:
    """The seed's bar over decision rows (one per replayed result)."""
    pruned = [r for r in rows if r.get("pruned") is True]
    misses = [r for r in pruned if r.get("miss") is True]
    saved = sum(r.get("tokens_saved", 0.0) for r in pruned)
    cost = sum(r.get("miss_cost", 0) for r in misses)
    net = saved - cost
    rate = len(misses) / len(pruned) if pruned else None
    finite = math.isfinite(saved) and math.isfinite(cost) and math.isfinite(net)
    passed = bool(pruned) and finite and rate is not None and rate <= MISS_RATE_BAR and net > 0
    reasons = []
    if not pruned:
        reasons.append("no result was pruned, so net tokens saved = 0")
    elif rate is not None and rate > MISS_RATE_BAR:
        reasons.append(f"miss rate {rate:.4f} > {MISS_RATE_BAR}")
    if not finite:
        reasons.append("a non-finite total")
    elif pruned and net <= 0:
        reasons.append(f"net tokens {net:.1f} <= 0")
    return {
        "results": len(rows), "pruned": len(pruned), "misses": len(misses), "miss_rate": rate,
        "tokens_saved": saved, "miss_cost": cost, "net": net,
        "verdict": "PASS" if passed else "FAIL", "why": reasons,
    }
