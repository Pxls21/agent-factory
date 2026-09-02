<!-- DEFAULT TEMPLATE: Used when .wiki-compiler.json has no article_sections field.
     New projects get custom sections generated during /wiki-init based on actual source content. -->

<!-- TIME-DECAY GUIDANCE:
     Time-sensitive topics (AI tooling/architecture, UI patterns, growth tactics,
     any bookmark-heavy topic): 6mo → aging, 18mo → stale.
     Stable topics (career, visa, personal-growth): 24mo → aging, 48mo → stale.
     Apply:
     - Summary leads with the date range of sources
     - Timeline / Key Decisions ordered newest-first, date-prefixed, ⚠️ on stale
     - Sections resting on aging sources get "[as of YYYY-MM]" next to coverage tag
     - Never delete stale content — flag, re-order, or annotate -->

---
topic: {Topic Name}
last_compiled: {YYYY-MM-DD}
source_count: {number}
status: active
---

# {Topic Name}

## Summary [coverage: {high|medium|low} -- {N} sources]
{2-3 paragraph synthesis of everything known about this topic.
Written as a briefing -- someone reading just this section should
understand the current state without reading any source file.
Be specific with numbers, dates, and decisions -- not vague summaries.}

## Timeline [coverage: {high|medium|low} -- {N} sources]
{Key events in chronological order}
- **YYYY-MM-DD:** {What happened}

## Current State [coverage: {high|medium|low} -- {N} sources]
{What's true RIGHT NOW: active metrics, live experiments, open questions.
This section should be immediately actionable.}

## Key Decisions [coverage: {high|medium|low} -- {N} sources]
{Decisions that shaped current approach, with rationale}
- **YYYY-MM-DD:** {Decision} -- {Why}

## Experiments & Results [coverage: {high|medium|low} -- {N} sources]
| Experiment | Status | Finding | Source |
|------------|--------|---------|--------|

## Gotchas & Known Issues [coverage: {high|medium|low} -- {N} sources]
{Relevant known issues, traps, and workarounds.
Only include entries relevant to THIS topic.}

## Open Questions [coverage: {high|medium|low} -- {N} sources]
{Unresolved threads, gaps in knowledge, suggested next investigations.}

## Sources
{List ALL source files that contributed to this article}
- [[relative/path/to/source]]

---

## Coverage Guide

Coverage indicators help the reader (human or AI) decide whether to trust this section or read raw sources:

- **high** -- 5+ sources, detailed synthesis, recently compiled. Trust this section.
- **medium** -- 2-4 sources, decent coverage but may miss detail. Check raw sources for granular questions.
- **low** -- 1 source or sparse data. Read the raw sources listed below this section.
