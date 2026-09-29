#!/usr/bin/env python3
"""K1-COMPACTION-LOSS (task #352, D-106): what does a compaction lose, and does the work get worse as the context fills?

    compaction.py select --transcript MAIN --subagents DIR --sizes SIZES.json --out DIR
    compaction.py run --transcript FILE --pin BYTES --label NAME --out DIR [--sidechain]
    compaction.py summary --out DIR [--stamp STAMP]

The brief is tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md; the plan is docs/research/findings/jev-trim/
D105-DESIGN-v1.md §10.2 (R-B, R-C). It measures and recommends nothing. It imports scripts/jev_trim/replay.py (the
timeline: requests, segments opened by compact_boundary records, items with modeled sizes and P1 tokens) and
scripts/jev_pipes (the walker and accounting.miss) and modifies neither.

PINS (`select`): the main transcript, and every subagent transcript holding at least one compact_boundary record (a
parsed system record, never a text match), each at the size measured at the lane's start (--sizes), stepped back to a
record boundary. A subagent file that holds a boundary now but was not measured at the start is listed as not pinned.

R-C, THE LOSS AT EACH COMPACTION (every compact_boundary whose segments on both sides hold a request).
- Removed: the pre-boundary segment's items (every kind, modeled sizes); exact: its last request's context.
- Kept start: the post-boundary segment's items that entered before its first request (the summary record and the
  injections), modeled; exact: the first context and, where the boundary record holds it, postTokens.
- Windows: the next N requests of the post segment, N in WINDOWS (20, 100, the rest of the segment); the used tokens
  are the P1 tokens of the tool inputs and assistant texts those requests produced.
- The P1 miss: accounting.miss with original = the pre segment's text, kept = the kept start's text, history = the
  post segment's prompt_snapshot tokens (the system prompt and tools, which a compaction keeps) and the window's used
  tokens as the lookahead. The set is computed over the tokens accounting.tokens gave each item (see _miss); once per
  boundary, at the widest window, accounting.miss is called on the two full texts and its count must equal the set's
  size (else the run stops). Paths: missed tokens that hold a "/" and fullmatch accounting's path class; for each,
  whether the pre segment Read or edited a file with that path (equal, or the file path ends with "/" + the token).
- Reused: the pre segment's tokens the window used whether or not the kept start held them (the miss is part of it).
- Re-fetches: each window tool call counted once, under the first shape it matches (SHAPES): read_known_path (a Read of
  a file the pre segment read or edited; `reinjected` counts those whose file the kept start re-injected),
  rerun_command (a Bash command equal, whitespace folded, to one the pre segment ran), identical_other_call (another
  tool called with the same input as in the pre segment; not Read, Bash or an edit), search_transcript, search_ledger,
  search_live_state (the call's input names one of SEARCH_MARKERS). Cost: the calls' input and result tokens (modeled)
  and the number of requests that made them.
- The control: one pseudo-boundary per segment of at least 2 x PSEUDO_GAP requests, at its middle request (so at
  least PSEUDO_GAP requests from either end, and from any real boundary). Original = the segment's items before it;
  kept = everything still in context, the same items, so the miss is 0 by construction (checked); reused and the
  re-fetches (against the segment's calls before it) give the base rate. Excess = the real mean minus the control mean.
- Class: a boundary whose pre segment's last context is under CLASS_SPLIT is `200k_window` (the session's early
  segments), else `1M_window`.

R-B, THE QUALITY CURVE (a streaming pass with the walker's primitives). Each tool call takes the fill of the request
that made it (input + cache creation + cache read of the request's first usage record). Per 100k bin, per segment third
(by request position) and per model and bin: calls, tool errors by tool (is_error), failed edits (EDIT_TOOLS with an
error result), re-reads (a Read with the file_path, offset and limit of an earlier Read in the segment and no edit call
on that file between: the coordinator's probe's key), re-runs (a Bash command equal to an earlier one in the segment
with no edit call on any file between) and hook refusals by gate (GATES: a fixed marker at a line start, or inside an
error result for the PreToolUse intercept). An edit is an edit tool's call, failed or not (as the probe); a Bash
command that changes a file is not seen.

THE COST MODEL (a model; every assumption is in MODEL_ASSUMPTIONS). For each compaction point X in COST_POINTS, the
growth of the included segments (each request's exact context minus the previous one's in the same segment) is replayed
as one stream from the kept start K (the mean first context of the included segments that open at a boundary); when
the fill would pass X a compaction is counted and the fill returns to K. It reports the modeled compactions, the mean
fill per request, the context, cache-read and cache-write tokens and their units at READ_RATIO and WRITE_RATIO, and the
modeled loss: the compactions times the run's mean per-boundary miss and re-fetches (1M_window class), raw and as the
excess over the control.

Outputs carry counts, sizes, offsets, ids and tool, kind, rule, shape, gate and model names only; token sets live in
memory and are never printed or stored.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import datetime
import json
import math
import os
import re
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jev_pipes import accounting, transcript  # noqa: E402
from jev_trim import replay  # noqa: E402

WINDOWS = (20, 100, None)  # None: the rest of the segment
PSEUDO_GAP = 100
FILL_BIN = 100_000
CLASS_SPLIT = 400_000
COST_POINTS = (300_000, 400_000, 500_000, 600_000, 700_000, 785_000)
READ_RATIO = 0.05
WRITE_RATIO = replay.CACHE_WRITE_1H
EDIT_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
FILE_KEYS = ("file_path", "notebook_path")
LOOK_KINDS = frozenset({"tool_input", "assistant_text"})
REINJECTED_TYPES = frozenset({"file", "compact_file_reference", "edited_text_file"})
SHAPES = ("read_known_path", "rerun_command", "identical_other_call", "search_transcript", "search_ledger",
          "search_live_state")
SEARCH_MARKERS = {  # shape: marker groups; a group matches when all its strings are in the call's input
    "search_transcript": ((".claude/projects/",), ("/tasks/", ".output"), ("chat_tail.py",), ("session_export.py",),
                          ("transcript_export.py",), ("hiccup_scan.py",), ("replay_transcript_edits.py",)),
    "search_ledger": (("BUILD-TASKLIST.md",),),
    "search_live_state": (("live-state.md",),),
}
GATES = (  # (gate, marker, rule): "line" = the marker opens a line of the result; "error" = in a result with is_error
    ("future_stamp", "COMMIT BLOCKED by the future-stamp gate", "line"),
    ("lint_delta", "COMMIT BLOCKED by lint_delta", "line"),
    ("mutant_anchor", "COMMIT BLOCKED by mutant_anchor_precommit", "line"),
    ("mirror", "COMMIT BLOCKED by the MIRROR gate", "line"),
    ("never_a_gate", "COMMIT BLOCKED by the never-a-gate screen", "line"),
    ("push_in_flight", "COMMIT BLOCKED: a push is in flight", "line"),
    ("commit_blocked_other", "COMMIT BLOCKED", "line"),
    ("push_blocked", "PUSH BLOCKED", "line"),
    ("stale_ids", "REFUSED by stale_ids", "line"),
    ("ci_gate", "REFUSED by ci-gate", "line"),
    ("search_intercept", "SEARCH INTERCEPT (search-intercept.py)", "error"),
    ("quirk_guard", "QUIRK GUARD (search-intercept.py", "error"),
)
_GATE_RE = {gate: re.compile("(?m)^" + re.escape(marker)) for gate, marker, rule in GATES if rule == "line"}
MODEL_ASSUMPTIONS = (
    "A model, not a measurement: the session's work (its per-request growth) is taken as the same at every X.",
    "Included: the segments that do not end in a compaction under CLASS_SPLIT (the early 200k-window segments are "
    "left out); their growth steps are replayed in file order as one stream.",
    "The step across an observed compaction is taken as 0 (the real step is the compaction's drop).",
    "After a modeled compaction the fill returns to K, the mean first context of the included segments that open at a "
    "boundary, whatever X is.",
    "A compaction is counted when the fill would pass X; the request after it sends K, all of it written to the cache "
    "(the system prompt's cached prefix is not credited).",
    "Every other request reads the previous request's fill from the cache and writes what it adds (a negative step "
    "writes nothing); cache reads are priced at READ_RATIO, writes at WRITE_RATIO, of the base input price.",
    "The summarizer's own call (it reads the whole context once per compaction) is reported as its own column, not "
    "added to the reads.",
    "The loss per compaction is the run's mean per-boundary value (1M_window class) measured at about 785k, the same "
    "at every X; `rest` keeps the observed segment length.",
)


# ---------------------------------------------------------------- pins

def pin_of(path: str, size: int | None = None) -> int:
    """The byte length up to the last record boundary (a newline) at or before `size` (default: the file's size)."""
    size = os.path.getsize(path) if size is None else size
    with open(path, "rb") as handle:
        end = size
        while end > 0:
            start = max(0, end - 65536)
            handle.seek(start)
            chunk = handle.read(end - start)
            cut = chunk.rfind(b"\n")
            if cut >= 0:
                return start + cut + 1
            end = start
    return 0


def boundary_records(path: str, pin: int, sidechain: bool) -> int:
    """compact_boundary system records on the thread within the pin (parsed records, never a text match)."""
    stats: collections.Counter = collections.Counter()
    count = 0
    for _, record in transcript.iter_records(path, pin, stats):
        side = record.get("isSidechain")
        if isinstance(side, bool) and side is not sidechain:
            continue
        if record.get("type") == "system" and record.get("subtype") == "compact_boundary":
            count += 1
    return count


def select(main: str, subagents: str, sizes: dict) -> dict:
    """The pin list: main, and every subagent file with a boundary record within its start size."""
    rows = [{"file": Path(main).name, "role": "main", "measured": sizes.get(Path(main).name),
             "pin": pin_of(main, sizes.get(Path(main).name)), "sidechain": False}]
    rows[0]["boundaries"] = boundary_records(main, rows[0]["pin"], False)
    later = []
    for name in sorted(os.listdir(subagents)):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(subagents, name)
        if name in sizes:
            pin = pin_of(path, sizes[name])
            count = boundary_records(path, pin, True)
            if count:
                rows.append({"file": name, "role": "subagent", "measured": sizes[name], "pin": pin, "sidechain": True,
                             "boundaries": count})
        elif boundary_records(path, pin_of(path), True):
            later.append(name)  # a boundary now, but not in the start measurement
    return {"pins": rows, "not_pinned_with_a_boundary_now": later}


# ---------------------------------------------------------------- R-C

@dataclass
class Facts:
    """What the items before a boundary held: tokens, the files read and edited, the calls made."""
    tokens: frozenset = frozenset()
    reads: set = field(default_factory=set)
    edits: set = field(default_factory=set)
    commands: set = field(default_factory=set)
    calls: set = field(default_factory=set)
    kinds: collections.Counter = field(default_factory=collections.Counter)


def _call_input(item: replay.Item) -> dict:
    try:
        value = json.loads(item.text) if item.text else None
    except ValueError:
        value = None
    return value if isinstance(value, dict) else {}


def _file_of(item: replay.Item) -> str | None:
    tool_input = _call_input(item)
    for key in FILE_KEYS:
        if isinstance(tool_input.get(key), str):
            return tool_input[key]
    return None


def facts(items: list) -> Facts:
    out = Facts()
    tokens = set()
    for it in items:
        tokens |= it.toks
        out.kinds[it.kind] += it.size
        if it.kind != "tool_input":
            continue
        if it.name == "Read":
            path = _file_of(it)
            if path:
                out.reads.add(path)
        elif it.name in EDIT_TOOLS:
            path = _file_of(it)
            if path:
                out.edits.add(path)
        elif it.name == "Bash":
            out.commands.add(it.rerun)
        elif it.rerun is not None:
            out.calls.add(it.rerun)
    out.tokens = frozenset(tokens)
    return out


def _shape(it: replay.Item, pre: Facts) -> str | None:
    """The re-fetch shape of one window call (the first that matches), or None."""
    if it.name == "Read" and _file_of(it) in (pre.reads | pre.edits):
        return "read_known_path"
    if it.name == "Bash" and it.rerun in pre.commands:
        return "rerun_command"
    if it.name not in ("Read", "Bash") and it.name not in EDIT_TOOLS and it.rerun in pre.calls:
        return "identical_other_call"
    text = it.text or ""
    for shape, groups in SEARCH_MARKERS.items():
        if any(all(marker in text for marker in group) for group in groups):
            return shape
    return None


def _names_file(token: str, files: set) -> bool:
    return any(f == token or (not token.startswith("/") and f.endswith("/" + token)) for f in files)


def _miss(original: frozenset, kept: frozenset, history: frozenset, used: frozenset,
          texts: tuple[str, str] | None = None) -> set:
    """The missed tokens: (original - kept - history) & used, over the tokens accounting.tokens gave each item.

    The union of an item list's tokens equals accounting.tokens of its texts joined by newlines (no class matches
    across a newline, and a newline is a word boundary), so the set is accounting.miss's own. With `texts` (the
    original's and the kept start's texts, each joined by newlines) accounting.miss is called on them and its count must
    equal the set's size, else the run stops. A call on texts cut down to the used tokens is NOT the same: Python's \\b
    counts a non-ASCII letter as a word character, so a path's inner identifier can match alone and not in its text."""
    missed = set((original - kept - history) & used)
    if texts is not None:
        count, _ = accounting.miss(texts[0], texts[1], history, [used], [], None)
        if count != len(missed):
            raise AssertionError(f"accounting.miss counted {count}, the set holds {len(missed)}")
    return missed


def measure(original: frozenset, kept: frozenset, history: frozenset, look: list, calls: list, pre: Facts,
            results: dict, producer, reinjected: set, texts: tuple[str, str] | None = None) -> dict:
    """One boundary (or pseudo-boundary) and one window: the miss, the reuse, the missed paths, the re-fetches."""
    used = frozenset().union(*(it.toks for it in look)) if look else frozenset()
    missed = _miss(original, kept, history, used, texts)
    paths = [t for t in missed if "/" in t and accounting._PATH.fullmatch(t)]
    edited = sum(1 for t in paths if _names_file(t, pre.edits))
    read = sum(1 for t in paths if not _names_file(t, pre.edits) and _names_file(t, pre.reads))
    shapes: dict = {s: {"calls": 0, "tokens": 0.0, "requests": set()} for s in SHAPES}
    reinjected_reads = 0
    for it in calls:
        shape = _shape(it, pre)
        if shape is None:
            continue
        row = shapes[shape]
        row["calls"] += 1
        row["tokens"] += it.size + (results[it.tool_use_id].size if it.tool_use_id in results else 0.0)
        row["requests"].add(producer(it))
        if shape == "read_known_path" and _file_of(it) in reinjected:
            reinjected_reads += 1
    all_requests = set().union(*(row["requests"] for row in shapes.values()))
    return {"used": len(used), "reused": len((original - history) & used), "missed": len(missed),
            "missed_paths": len(paths), "missed_paths_edited_before": edited, "missed_paths_read_before": read,
            "missed_paths_neither": len(paths) - edited - read,
            "refetch": {s: {"calls": row["calls"], "tokens": round(row["tokens"], 1), "requests": len(row["requests"])}
                        for s, row in shapes.items()},
            "refetch_total": {"calls": sum(row["calls"] for row in shapes.values()),
                              "tokens": round(math.fsum(row["tokens"] for row in shapes.values()), 1),
                              "requests": len(all_requests)},
            "read_known_path_reinjected": reinjected_reads}


def _window(segment: replay.Segment, pos: int, n: int | None) -> tuple[list, list, int]:
    """The lookahead items and the tool calls that requests pos .. pos+n-1 of the segment produced, and n clipped."""
    offsets = [r.offset for r in segment.requests]
    end = len(offsets) if n is None else min(len(offsets), pos + n)
    lo = offsets[pos]
    hi = offsets[end] if end < len(offsets) else float("inf")
    look, calls = [], []
    for it in segment.items:
        if lo <= it.offset < hi:
            if it.kind in LOOK_KINDS:
                look.append(it)
            if it.kind == "tool_input":
                calls.append(it)
    return look, calls, end - pos


def _producer(segment: replay.Segment):
    offsets = [r.offset for r in segment.requests]
    return lambda it: bisect.bisect_right(offsets, it.offset) - 1


def _label(n: int | None) -> str:
    return "rest" if n is None else str(n)


def _post_tokens(segment: replay.Segment) -> int | None:
    value = segment.fixed_estimates.get("first_context_minus_post_tokens")
    return None if value is None else round(segment.requests[0].context - value)


def compaction_loss(tl: replay.Timeline) -> dict:
    """R-C at every boundary with requests on both sides, and the control at the pseudo-boundaries."""
    by_index = {s.index: s for s in tl.segments}
    rows, skipped = [], []
    for k, (offset, day) in enumerate(tl.boundaries, start=1):
        pre, post = by_index.get(k - 1), by_index.get(k)
        if pre is None or post is None:
            skipped.append({"boundary": k, "offset": offset, "pre_has_requests": pre is not None,
                            "post_has_requests": post is not None})
            continue
        opening = [it for it in post.items if it.start]
        pre_facts, kept = facts(pre.items), facts(opening)
        reinjected = {it.attach_key[1] for it in opening
                      if it.attach_type in REINJECTED_TYPES and it.attach_key and len(it.attach_key) > 1}
        results = {it.tool_use_id: it for it in post.items if it.kind == "tool_result" and it.tool_use_id}
        producer = _producer(post)
        texts = ("\n".join(it.text for it in pre.items if it.text is not None),
                 "\n".join(it.text for it in opening if it.text is not None))
        windows = {}
        for n in WINDOWS:
            look, calls, length = _window(post, 0, n)
            # accounting.miss on the full texts, once per boundary: at the widest window
            windows[_label(n)] = {"requests": length, **measure(pre_facts.tokens, kept.tokens, post.fixed, look, calls,
                                                                 pre_facts, results, producer, reinjected,
                                                                 texts if n is None else None)}
        last = pre.requests[-1].context
        rows.append({"boundary": k, "offset": offset, "day": day,
                     "class": "200k_window" if last < CLASS_SPLIT else "1M_window",
                     "pre": {"segment": pre.index, "requests": len(pre.requests), "last_context": last,
                             "tokens_modeled": round(math.fsum(pre_facts.kinds.values()), 1),
                             "tokens_by_kind": {kd: round(v, 1) for kd, v in sorted(pre_facts.kinds.items())},
                             "files_read": len(pre_facts.reads), "files_edited": len(pre_facts.edits),
                             "commands": len(pre_facts.commands), "distinct_tokens": len(pre_facts.tokens)},
                     "kept": {"items": len(opening), "tokens_modeled": round(math.fsum(kept.kinds.values()), 1),
                              "tokens_by_kind": {kd: round(v, 1) for kd, v in sorted(kept.kinds.items())},
                              "first_context": post.requests[0].context, "post_tokens": _post_tokens(post),
                              "files_reinjected": len(reinjected), "distinct_tokens": len(kept.tokens)},
                     "post_requests": len(post.requests), "windows": windows})
    control = []
    for segment in tl.segments:
        n = len(segment.requests)
        if n < 2 * PSEUDO_GAP:
            continue
        mid = n // 2
        split = segment.requests[mid].offset
        before = [it for it in segment.items if it.offset < split]
        pre_facts = facts(before)
        results = {it.tool_use_id: it for it in segment.items if it.kind == "tool_result" and it.tool_use_id}
        producer = _producer(segment)
        windows = {}
        for w in WINDOWS:
            look, calls, length = _window(segment, mid, w)
            # nothing was removed: kept = everything still in context = the same items as the original
            windows[_label(w)] = {"requests": length, **measure(pre_facts.tokens, pre_facts.tokens, segment.fixed, look,
                                                                calls, pre_facts, results, producer, set())}
        control.append({"segment": segment.index, "requests": n, "position": mid, "offset": split,
                        "class": _segment_class(tl, segment), "windows": windows})
    return {"boundaries": rows, "skipped": skipped, "control": control}


def _ends_in_compaction(tl: replay.Timeline, segment: replay.Segment) -> bool:
    last = segment.requests[-1].offset
    return any(offset > last for offset, _ in tl.boundaries)


def _segment_class(tl: replay.Timeline, segment: replay.Segment) -> str:
    small = _ends_in_compaction(tl, segment) and segment.requests[-1].context < CLASS_SPLIT
    return "200k_window" if small else "1M_window"


# ---------------------------------------------------------------- R-B

def _gate(text: str, is_error: bool) -> str | None:
    for gate, marker, rule in GATES:
        if rule == "line" and _GATE_RE[gate].search(text):
            return gate
        if rule == "error" and is_error and marker in text:
            return gate
    return None


def _counter() -> dict:
    return {"requests": 0, "calls": 0, "errors": 0, "errors_by_tool": collections.Counter(), "edits": 0,
            "failed_edits": 0, "reads": 0, "rereads": 0, "bash": 0, "reruns": 0,
            "refusals_by_gate": collections.Counter(), "calls_without_a_result": 0, "fill_sum": 0}


def quality(path: str, pin: int, sidechain: bool = False) -> dict:
    """R-B: the no-judge signals per 100k bin of fill, per segment third and per model and bin."""
    stats: collections.Counter = collections.Counter()
    requests: dict = {}  # requestId -> [fill, segment, model]
    calls: dict = {}
    order: list = []
    seg = 0
    reads: dict = {}
    commands: dict = {}
    edits = 0
    for offset, record in transcript.iter_records(path, pin, stats):
        side = record.get("isSidechain")
        if isinstance(side, bool) and side is not sidechain:
            continue
        kind = record.get("type")
        if kind == "system" and record.get("subtype") == "compact_boundary":
            seg += 1
            reads, commands, edits = {}, {}, 0
            continue
        if kind == "assistant":
            message = record.get("message") if isinstance(record.get("message"), dict) else {}
            if message.get("model") == "<synthetic>":
                continue
            rid = record.get("requestId") if isinstance(record.get("requestId"), str) else ""
            usage = message.get("usage")
            if rid and rid not in requests and isinstance(usage, dict):
                parts = [usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                                  "cache_read_input_tokens")]
                if all(type(v) is int and v >= 0 for v in parts):
                    requests[rid] = [sum(parts), seg, replay.safe_name(message.get("model"))]
            for block in transcript._blocks(record):
                if block.get("type") != "tool_use":
                    continue
                name = replay.safe_name(block.get("name"))
                tool_input = block.get("input") if isinstance(block.get("input"), dict) else {}
                call = {"rid": rid, "seg": seg, "name": name, "error": None, "gate": None, "reread": False,
                        "rerun": False}
                if name == "Read":
                    key = (tool_input.get("file_path"), tool_input.get("offset"), tool_input.get("limit"))
                    call["reread"] = reads.get(key) == "clean"
                    reads[key] = "clean"
                elif name in EDIT_TOOLS:
                    edits += 1
                    target = next((tool_input.get(k) for k in FILE_KEYS if isinstance(tool_input.get(k), str)), None)
                    for key in reads:
                        if key[0] == target:
                            reads[key] = "changed"
                elif name == "Bash":
                    key = transcript.rerun_key("Bash", tool_input)
                    call["rerun"] = commands.get(key) == edits
                    commands[key] = edits
                if isinstance(block.get("id"), str):
                    calls[block["id"]] = call
                order.append(call)
            continue
        if kind == "user":
            for block in transcript._blocks(record):
                if block.get("type") != "tool_result":
                    continue
                call = calls.get(block.get("tool_use_id"))
                if call is None:
                    stats["results_without_a_known_call"] += 1
                    continue
                call["error"] = block.get("is_error") is True
                call["gate"] = _gate(transcript.result_text(block), call["error"])
    positions: dict = collections.defaultdict(list)
    for rid, (fill, s, model) in requests.items():
        positions[s].append(rid)
    third = {}
    for s, rids in positions.items():
        for i, rid in enumerate(rids):
            third[rid] = ("first", "middle", "last")[i * 3 // len(rids)] if len(rids) >= 3 else None
    bins: dict = collections.defaultdict(_counter)
    thirds: dict = collections.defaultdict(_counter)
    by_model: dict = collections.defaultdict(_counter)
    for rid, (fill, s, model) in requests.items():
        for table, key in ((bins, fill // FILL_BIN), (thirds, third[rid]), (by_model, (model, fill // FILL_BIN))):
            if key is not None:
                table[key]["requests"] += 1
                table[key]["fill_sum"] += fill
    unattributed = 0
    for call in order:
        request = requests.get(call["rid"])
        if request is None:
            unattributed += 1
            continue
        fill, s, model = request
        for table, key in ((bins, fill // FILL_BIN), (thirds, third[call["rid"]]), (by_model, (model, fill // FILL_BIN))):
            if key is None:
                continue
            row = table[key]
            row["calls"] += 1
            if call["error"] is None:
                row["calls_without_a_result"] += 1
            elif call["error"]:
                row["errors"] += 1
                row["errors_by_tool"][call["name"]] += 1
            if call["name"] in EDIT_TOOLS:
                row["edits"] += 1
                row["failed_edits"] += call["error"] is True
            elif call["name"] == "Read":
                row["reads"] += 1
                row["rereads"] += call["reread"]
            elif call["name"] == "Bash":
                row["bash"] += 1
                row["reruns"] += call["rerun"]
            if call["gate"]:
                row["refusals_by_gate"][call["gate"]] += 1

    def dump(row: dict) -> dict:
        out = {k: (dict(sorted(v.items())) if isinstance(v, collections.Counter) else v) for k, v in row.items()
               if k != "fill_sum"}
        out["mean_fill"] = round(row["fill_sum"] / row["requests"], 1) if row["requests"] else None
        return out

    return {"bins": {f"{b * 100}k-{b * 100 + 100}k": dump(bins[b]) for b in sorted(bins)},
            "thirds": {t: dump(thirds[t]) for t in ("first", "middle", "last") if t in thirds},
            "by_model": {f"{m} {b * 100}k-{b * 100 + 100}k": dump(by_model[(m, b)]) for m, b in sorted(by_model)},
            "calls": len(order), "calls_without_a_request": unattributed, "requests": len(requests),
            "segments_with_requests": len(positions),
            "stats": dict(sorted((k, v) for k, v in stats.items()
                                 if k in ("unparseable_lines", "truncated_at_limit", "results_without_a_known_call")))}


# ---------------------------------------------------------------- the cost model

def _loss_means(rc: dict, cls: str = "1M_window") -> dict:
    """Per window: the mean per-boundary miss and re-fetch counts of the class, raw and as the excess over the
    control (the control's pseudo-boundaries of the same class)."""
    real = [r for r in rc["boundaries"] if r["class"] == cls]
    ctrl = [c for c in rc["control"] if c["class"] == cls]
    out = {}
    for n in WINDOWS:
        label = _label(n)
        means = {}
        for name, rows in (("real", real), ("control", ctrl)):
            if not rows:
                means[name] = None
                continue
            ws = [r["windows"][label] for r in rows]
            means[name] = {"boundaries": len(ws), "missed": statistics.fmean(w["missed"] for w in ws),
                           "missed_paths": statistics.fmean(w["missed_paths"] for w in ws),
                           "refetch_calls": statistics.fmean(w["refetch_total"]["calls"] for w in ws),
                           "refetch_tokens": statistics.fmean(w["refetch_total"]["tokens"] for w in ws),
                           "refetch_requests": statistics.fmean(w["refetch_total"]["requests"] for w in ws)}
        excess = None
        if means["real"] and means["control"]:
            excess = {k: means["real"][k] - means["control"][k] for k in means["real"] if k != "boundaries"}
        out[label] = {**means, "excess": excess}
    return out


def simulate(steps: list[float], kept: float, point: float) -> dict:
    """The one-stream model at compaction point `point` (see MODEL_ASSUMPTIONS): the stream starts at `kept`; a step
    that would carry the fill past the point is a compaction and the fill returns to `kept`."""
    fill = float(kept)
    total, reads, writes, summarizer = fill, 0.0, fill, 0.0
    compactions = 0
    for step in steps:
        if fill + step > point:
            compactions += 1
            summarizer += fill
            fill = float(kept)
            writes += fill
        else:
            reads += fill
            writes += max(0.0, step)
            fill += step
        total += fill
    requests = len(steps) + 1
    return {"compactions": compactions, "requests": requests, "mean_fill": round(total / requests, 1),
            "context_tokens": round(total, 1), "cache_read_tokens": round(reads, 1),
            "cache_write_tokens": round(writes, 1), "summarizer_read_tokens": round(summarizer, 1)}


def cost_model(tl: replay.Timeline, rc: dict) -> dict:
    included = [s for s in tl.segments if _segment_class(tl, s) == "1M_window"]
    excluded = [s.index for s in tl.segments if _segment_class(tl, s) != "1M_window"]
    steps: list[float] = []
    for i, segment in enumerate(included):
        if i:
            steps.append(0.0)  # the step across an observed compaction
        contexts = [r.context for r in segment.requests]
        steps.extend(float(b - a) for a, b in zip(contexts, contexts[1:]))
    starts = [s.requests[0].context for s in included if s.index >= 1]
    if not included or not starts:
        return {"included_segments": len(included), "rows": [], "assumptions": list(MODEL_ASSUMPTIONS)}
    kept = statistics.fmean(starts)
    losses = _loss_means(rc)
    observed = sum(1 for s in included if _ends_in_compaction(tl, s))
    rows = []
    for point in COST_POINTS:
        row = {"X": point, **simulate(steps, kept, point)}
        row["cache_read_units"] = round(READ_RATIO * row["cache_read_tokens"], 1)
        row["cache_write_units"] = round(WRITE_RATIO * row["cache_write_tokens"], 1)
        row["loss"] = {label: {kind: (None if value is None else
                                      {k: round(v * row["compactions"], 1) for k, v in value.items()
                                       if k != "boundaries"})
                               for kind, value in (("raw", m["real"]), ("excess", m["excess"]))}
                       for label, m in losses.items()}
        rows.append(row)
    return {"model": "MODEL, not a measurement", "included_segments": len(included), "excluded_segments": excluded,
            "kept_start_mean": round(kept, 1), "kept_start_from_segments": len(starts),
            "observed_compactions_in_included": observed, "steps": len(steps),
            "negative_steps": sum(1 for s in steps if s < 0), "loss_means_per_boundary": losses, "rows": rows,
            "read_ratio": READ_RATIO, "write_ratio": WRITE_RATIO, "assumptions": list(MODEL_ASSUMPTIONS)}


# ---------------------------------------------------------------- the run and the summary

def run(path: str, pin: int, label: str, sidechain: bool) -> dict:
    tl = replay.build(path, pin, sidechain=sidechain)
    rc = compaction_loss(tl)
    rb = quality(path, pin, sidechain)
    models = collections.Counter(q.model for q in tl.requests)
    return {"schema": 1, "label": label, "transcript": Path(path).name, "pin": pin, "sidechain": sidechain,
            "params": {"windows": [_label(n) for n in WINDOWS], "pseudo_gap": PSEUDO_GAP, "fill_bin": FILL_BIN,
                       "class_split": CLASS_SPLIT, "cost_points": list(COST_POINTS), "shapes": list(SHAPES),
                       "search_markers": {k: [list(g) for g in v] for k, v in SEARCH_MARKERS.items()},
                       "gates": [{"gate": g, "marker": m, "rule": r} for g, m, r in GATES],
                       "user_cpt": replay.USER_CPT, "stub_tokens": replay.STUB_TOKENS},
            "timeline": {"requests": len(tl.requests), "segments_with_requests": len(tl.segments),
                         "boundaries_on_the_thread": len(tl.boundaries),
                         "requests_by_model": dict(sorted(models.items())),
                         "stats": dict(sorted(tl.stats.items()))},
            "rc": rc, "quality": rb, "cost_model": cost_model(tl, rc)}


def _mean(values: list):
    return round(statistics.fmean(values), 2) if values else None


def _num(value, digits: int = 0) -> str:
    return "—" if value is None else f"{value:,.{digits}f}"


def _rc_table(rows: list, control: list) -> list[str]:
    lines = ["| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited "
             "before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) "
             "| control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) "
             "| excess missed | excess re-fetch calls | excess re-fetch tokens |", "|" + "---|" * 17]
    for n in WINDOWS:
        label = _label(n)
        ws = [r["windows"][label] for r in rows]
        cs = [c["windows"][label] for c in control]
        real_m = [w["missed"] for w in ws]
        ctrl_m = [w["missed"] for w in cs]
        real_c = [w["refetch_total"]["calls"] for w in ws]
        ctrl_c = [w["refetch_total"]["calls"] for w in cs]
        real_t = [w["refetch_total"]["tokens"] for w in ws]
        ctrl_t = [w["refetch_total"]["tokens"] for w in cs]

        def diff(a, b):
            return None if not a or not b else round(statistics.fmean(a) - statistics.fmean(b), 2)
        lines.append("| " + " | ".join([
            label, str(len(ws)), _num(_mean([w["requests"] for w in ws]), 1), _num(_mean(real_m), 1),
            _num(_mean([w["missed_paths"] for w in ws]), 1),
            f"{sum(w['missed_paths_read_before'] for w in ws)} / {sum(w['missed_paths_edited_before'] for w in ws)}",
            _num(_mean([w["reused"] for w in ws]), 1), _num(_mean(real_c), 2), _num(_mean(real_t), 1),
            _num(_mean([w["refetch_total"]["requests"] for w in ws]), 2), str(len(cs)),
            _num(_mean([w["reused"] for w in cs]), 1), _num(_mean(ctrl_c), 2), _num(_mean(ctrl_t), 1),
            _num(diff(real_m, ctrl_m), 1), _num(diff(real_c, ctrl_c), 2), _num(diff(real_t, ctrl_t), 1)]) + " |")
    return lines


def _shape_table(rows: list, control: list) -> list[str]:
    lines = ["| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | "
             "control tokens (sum) |", "|---|---|---|---|---|---|---|"]
    for n in WINDOWS:
        label = _label(n)
        for shape in SHAPES:
            real = [r["windows"][label]["refetch"][shape] for r in rows]
            ctrl = [c["windows"][label]["refetch"][shape] for c in control]
            lines.append(f"| {label} | {shape} | {sum(x['calls'] for x in real)} | "
                         f"{_num(math.fsum(x['tokens'] for x in real))} | {sum(x['requests'] for x in real)} | "
                         f"{sum(x['calls'] for x in ctrl)} | {_num(math.fsum(x['tokens'] for x in ctrl))} |")
    return lines


def _pct(a: int, b: int) -> str:
    return "—" if not b else f"{100 * a / b:.2f}%"


THIRDS = ("first", "middle", "last")


def _pool(tables: list[dict]) -> dict:
    """The sum of several runs' R-B tables, key by key (the mean fill weighted by requests)."""
    out: dict = {}
    for table in tables:
        for key, row in table.items():
            acc = out.setdefault(key, {"requests": 0, "calls": 0, "errors": 0, "errors_by_tool": collections.Counter(),
                                       "edits": 0, "failed_edits": 0, "reads": 0, "rereads": 0, "bash": 0, "reruns": 0,
                                       "refusals_by_gate": collections.Counter(), "calls_without_a_result": 0,
                                       "fill_sum": 0.0})
            for name in ("requests", "calls", "errors", "edits", "failed_edits", "reads", "rereads", "bash", "reruns",
                         "calls_without_a_result"):
                acc[name] += row[name]
            acc["errors_by_tool"].update(row["errors_by_tool"])
            acc["refusals_by_gate"].update(row["refusals_by_gate"])
            acc["fill_sum"] += (row["mean_fill"] or 0.0) * row["requests"]
    for acc in out.values():
        acc["mean_fill"] = round(acc.pop("fill_sum") / acc["requests"], 1) if acc["requests"] else None
    return out


def _bin_order(key: str) -> tuple:
    return (THIRDS.index(key), 0) if key in THIRDS else (len(THIRDS), int(key.split("k-")[0]))


def _quality_rows(table: dict, label: str = "bin") -> list[str]:
    table = {k: table[k] for k in sorted(table, key=_bin_order)}
    lines = [f"| {label} | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads "
             "| re-runs / Bash | refusals by gate | errors by tool (top 3) |", "|" + "---|" * 11]
    for key, r in table.items():
        top = ", ".join(f"{t} {n}" for t, n in sorted(r["errors_by_tool"].items(), key=lambda kv: -kv[1])[:3])
        gates = ", ".join(f"{g} {n}" for g, n in sorted(r["refusals_by_gate"].items()))
        lines.append(f"| {key} | {r['requests']:,} | {_num(r['mean_fill'])} | {r['calls']:,} | {r['errors']} | "
                     f"{_pct(r['errors'], r['calls'])} | {r['failed_edits']} / {r['edits']} "
                     f"({_pct(r['failed_edits'], r['edits'])}) | {r['rereads']} / {r['reads']} "
                     f"({_pct(r['rereads'], r['reads'])}) | {r['reruns']} / {r['bash']} "
                     f"({_pct(r['reruns'], r['bash'])}) | {gates or '0'} | {top or '—'} |")
    return lines


def _cost_rows(cm: dict) -> list[str]:
    lines = ["| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | "
             "write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | "
             "loss rest (raw) | loss N=100 (excess) |", "|" + "---|" * 13]

    def loss(value) -> str:
        if value is None:
            return "—"
        return f"{_num(value['missed'])} / {_num(value['refetch_calls'])} / {_num(value['refetch_tokens'])}"
    for row in cm["rows"]:
        lines.append(f"| {row['X']:,} | {row['compactions']} | {row['requests']:,} | {_num(row['mean_fill'])} | "
                     f"{_num(row['cache_read_tokens'])} | {_num(row['cache_read_units'])} | "
                     f"{_num(row['cache_write_tokens'])} | {_num(row['cache_write_units'])} | "
                     f"{_num(row['summarizer_read_tokens'])} | {loss(row['loss']['20']['raw'])} | "
                     f"{loss(row['loss']['100']['raw'])} | {loss(row['loss']['rest']['raw'])} | "
                     f"{loss(row['loss']['100']['excess'])} |")
    return lines


def write_summary(out: Path, stamp: str) -> Path:
    runs = sorted((json.loads(p.read_text()) for p in out.glob("run-*.json")),
                  key=lambda r: (r["sidechain"], r["label"]))
    pins = json.loads((out / "pins.json").read_text()) if (out / "pins.json").exists() else None
    lines = ["# K1-COMPACTION-LOSS results (task #352, D-106)", "",
             f"Written by `scripts/jev_trim/compaction.py summary` at {stamp}. Counts, sizes, offsets and names only.",
             "No recommendation. The brief is `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md`; the method is in the "
             "module's docstring.", ""]
    if pins:
        lines += ["## Pins", "", "| file | role | measured at the start | pin | compact_boundary records |",
                  "|---|---|---|---|---|"]
        lines += [f"| {p['file']} | {p['role']} | {_num(p['measured'])} | {p['pin']:,} | {p['boundaries']} |"
                  for p in pins["pins"]]
        lines += ["", f"Subagent files with a boundary now but not in the start measurement: "
                      f"{len(pins['not_pinned_with_a_boundary_now'])}.", ""]
    else:
        lines += ["## Pins: NO pins.json in this directory", ""]
    subagent_rows, subagent_control = [], []
    for run_ in runs:
        rc, rb, cm, t = run_["rc"], run_["quality"], run_["cost_model"], run_["timeline"]
        lines += [f"## Run `{run_['label']}`: {run_['transcript']} pinned at {run_['pin']:,} bytes "
                  f"({'sidechain' if run_['sidechain'] else 'main'} thread)", "",
                  f"- Requests {t['requests']:,}; segments with requests {t['segments_with_requests']}; boundaries on the "
                  f"thread {t['boundaries_on_the_thread']}; skipped boundaries {len(rc['skipped'])}; models "
                  f"{t['requests_by_model']}.", ""]
        if run_["sidechain"]:
            subagent_rows += rc["boundaries"]
            subagent_control += rc["control"]
        for cls in ("1M_window", "200k_window"):
            rows = [r for r in rc["boundaries"] if r["class"] == cls]
            control = [c for c in rc["control"] if c["class"] == cls]
            if not rows and not control:
                continue
            removed = _mean([r["pre"]["tokens_modeled"] for r in rows])
            kept = _mean([r["kept"]["tokens_modeled"] for r in rows])
            lines += [f"### R-C, class `{cls}`: {len(rows)} boundaries, {len(control)} control points", "",
                      f"- Removed per boundary (modeled, mean): {_num(removed)} tokens; last context before (mean) "
                      f"{_num(_mean([r['pre']['last_context'] for r in rows]))}; kept start per boundary (modeled, mean)"
                      f" {_num(kept)}; first context after (mean) "
                      f"{_num(_mean([r['kept']['first_context'] for r in rows]))}; postTokens (mean) "
                      f"{_num(_mean([r['kept']['post_tokens'] for r in rows if r['kept']['post_tokens'] is not None]))}.",
                      ""]
            lines += _rc_table(rows, control) + [""] + _shape_table(rows, control) + [""]
        lines += ["### R-B, per 100k of fill", ""] + _quality_rows(rb["bins"]) + ["", "### R-B, per segment third", ""]
        lines += _quality_rows(rb["thirds"], "third") + [""]
        lines += [f"### Cost model (MODEL, not a measurement): included segments {cm['included_segments']}, kept start "
                  f"{_num(cm.get('kept_start_mean'))}, observed compactions among them "
                  f"{cm.get('observed_compactions_in_included')}", ""]
        lines += _cost_rows(cm) + [""] if cm["rows"] else ["No included segment.", ""]
    sides = [r for r in runs if r["sidechain"]]
    if sides:
        lines += [f"## Subagent files pooled: {len(sides)} files, {len(subagent_rows)} boundaries, "
                  f"{len(subagent_control)} control points", "", "### R-C, pooled", ""]
        lines += _rc_table(subagent_rows, subagent_control) + [""] + _shape_table(subagent_rows, subagent_control)
        lines += ["", "### R-B, pooled, per 100k of fill", ""] + _quality_rows(_pool([r["quality"]["bins"] for r in sides]))
        lines += ["", "### R-B, pooled, per segment third", ""]
        lines += _quality_rows(_pool([r["quality"]["thirds"] for r in sides]), "third") + [""]
    if runs and runs[0]["cost_model"].get("assumptions"):
        lines += ["## The cost model's assumptions", ""] + [f"- {a}" for a in runs[0]["cost_model"]["assumptions"]]
        lines.append("")
    if runs:
        lines += ["## Markers", "", "Hook refusals (R-B), by gate:", ""]
        lines += [f"- `{g['gate']}`: `{g['marker']}` ({'at a line start' if g['rule'] == 'line' else 'in an error result'})"
                  for g in runs[0]["params"]["gates"]]
        lines += ["", "Searches (R-C re-fetch shapes):", ""]
        lines += [f"- `{shape}`: " + "; ".join(" and ".join(f"`{m}`" for m in group) for group in groups)
                  for shape, groups in runs[0]["params"]["search_markers"].items()]
        lines.append("")
    target = out / "SUMMARY.md"
    target.write_text("\n".join(lines) + "\n")
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("select", help="the pin list: main and the subagent files with a compact_boundary record")
    s.add_argument("--transcript", required=True)
    s.add_argument("--subagents", required=True)
    s.add_argument("--sizes", type=Path, required=True, help="JSON list of {file, pin}: the sizes measured at the start")
    s.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("run", help="R-C, the control, R-B and the cost model over one transcript")
    r.add_argument("--transcript", required=True)
    r.add_argument("--pin", type=int, required=True)
    r.add_argument("--label", required=True)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--sidechain", action="store_true")
    m = sub.add_parser("summary", help="SUMMARY.md from the JSON files in --out")
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--stamp", default=None)
    args = ap.parse_args(argv)
    if args.command == "summary":
        stamp = args.stamp or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print("wrote", write_summary(args.out, stamp))
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    if args.command == "select":
        sizes = {row["file"]: row["pin"] for row in json.loads(args.sizes.read_text())}
        result = select(args.transcript, args.subagents, sizes)
        (args.out / "pins.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        print(f"pins: {len(result['pins'])} files; not pinned with a boundary now: "
              f"{len(result['not_pinned_with_a_boundary_now'])}")
        return 0
    began = time.monotonic()
    result = run(args.transcript, args.pin, args.label, args.sidechain)
    target = args.out / f"run-{args.label}.json"
    target.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    rc = result["rc"]
    print(f"wrote {target}: {len(rc['boundaries'])} boundaries, {len(rc['control'])} control points, "
          f"{result['quality']['calls']} calls, {time.monotonic() - began:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
