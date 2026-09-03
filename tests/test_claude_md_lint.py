"""CLAUDE.md doc-lint (ported pattern from trading-system R5 FIND-29).

Two stale-claim classes this repo already knows about:
  1. CLAUDE.md must name todo/BUILD-TASKLIST.md as the SINGLE SOURCE OF TRUTH for live
     build status instead of re-stating (and re-staling) a count.
  2. The council's ledger rule: no flat "N/12" proof score anywhere a human reads status —
     classes carry separate denominators (COUNCIL-VERDICT-STAGE0-v1 KC-4).

Deterministic, LLM-free: substring/regex checks on committed files, no build code executed.
The negative control proves the scanners have teeth on planted text, never on tracked files."""
from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CLAUDE_MD = _ROOT / "CLAUDE.md"
_STATUS_SURFACES = [_ROOT / "CLAUDE.md", _ROOT / "todo" / "BUILD-TASKLIST.md", _ROOT / "tasks" / "stage0-breakdown.md"]

# "9/12 proven", "7 / 12 green", "11 of 12 proofs" — the flat-denominator shapes the council banned.
_FLAT_N_OF_12_RE = re.compile(r"\b\d{1,2}\s*(?:/|of)\s*12\s+(?:proofs?|proven|green|passing|done)\b", re.IGNORECASE)


def _has_flat_score(text: str) -> bool:
    return bool(_FLAT_N_OF_12_RE.search(text))


def test_claude_md_points_to_build_tasklist_as_single_source_of_truth():
    text = _CLAUDE_MD.read_text(encoding="utf-8")
    assert "SINGLE SOURCE OF TRUTH" in text
    assert "todo/BUILD-TASKLIST.md" in text


def test_status_surfaces_carry_no_flat_n_of_12_score():
    for p in _STATUS_SURFACES:
        if p.exists():
            assert not _has_flat_score(p.read_text(encoding="utf-8")), f"{p.name} carries a flat N/12 proof score"


def test_negative_control_scanner_detects_planted_flat_score():
    planted = "Status: 9/12 proofs green, ship it."
    assert _has_flat_score(planted)
    assert not _has_flat_score(planted.replace("9/12 proofs green", "7 execution proofs green, 2 blocked"))
