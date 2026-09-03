# bug-echo — project install notes (trading-system)

Vendored from github.com/Terryc21/bug-echo @ v1.3.2 (2026-07-22), Apache-2.0
(LICENSE + NOTICE preserved alongside). Reviewed line-by-line before install:
pure-markdown skill, no scripts, git-only Bash usage.

Project adaptations when invoking here:
- Output dir: pass `output=docs/research/bug-echo/` (house convention; the
  skill's `.agents/research/` default is another family's convention).
- AskUserQuestion: this repo's CLAUDE.md forbids blocking AskUserQuestion when
  the owner may be away — when running bug-echo autonomously, take the skill's
  "Recommended" option and note the choice in the report instead of blocking.
- Known first targets (our recurring fixed-bug classes, use described mode):
  1. fail-open numeric guards on externally-sourced values (`x <= 0` without
     `isfinite`; NaN wormhole family — DX8a, DX7-full, ST8, the pbo budget).
  2. metric-unavailable exceptions dropping whole evaluation windows
     (the B14 paper-gate class).
  3. per-invocation-vs-cumulative budget measurement in perpetual loops (ST8).
  4. engine-artifact gene bounds (the x58 TSL class, post degame-wave).
