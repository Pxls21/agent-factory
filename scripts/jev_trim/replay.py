#!/usr/bin/env python3
"""T0-REPLAY (task #346, D-105): replay plain, deterministic trimming rules over a Claude Code transcript.

    replay.py run --transcript FILE --pin BYTES --label NAME --out DIR [--start BYTES] [--sidechain]
                  [--modes M ...] [--turn-units U ...]
    replay.py crosscheck --transcript FILE --pin BYTES --audit AUDIT.md --out DIR
    replay.py summary --out DIR

The question (tasks/briefs/jev-trim/T0-REPLAY-brief.md): under the policy of docs/research/findings/jev-trim/
D105-DESIGN-v1.md §3.1, with no model deciding anything, what would the active context have been per API request, how
often would a trim have fired, what would the trims have cost the prompt cache, and how often did the session later
use something the rules would have archived? It measures and recommends nothing. Advisory; never a gate.

THE TIMELINE (`build`: one streaming pass with scripts/jev_pipes/transcript.iter_records, pinned at a byte length).
- A request is the first assistant record with a usage block of each requestId on the chosen thread, `<synthetic>`
  records excluded. The thread is `isSidechain` false for a main transcript; a subagent file holds sidechain records
  only, so its runs pass --sidechain. Whole context = input + cache creation + cache read (TRIM-AUDIT §3, the committed
  walker's definition); output = the largest output_tokens over the request's records.
- A segment starts at each system/compact_boundary record; every segment is simulated from its real start.
- Turns, both kept on every item and request: `stop` (after each stop_hook_summary or compact_boundary record) and
  `prompt` (a new promptId on a user record, or a compact_boundary). A turn id counts only turns that hold a request;
  an item in a turn with none joins the next turn that has one. The policy reads one unit (`request` makes every
  request its own turn).
- Items enter the context of the first request after their record in the same segment (an item after a segment's last
  request enters none): tool results (by tool), tool inputs (by tool), visible assistant text, thinking (one item per
  request), typed user text (the owner's or the coordinator's messages, queued prompts, a message without an origin),
  other user text (meta text such as skill bodies, notifications, the compaction summary), task reminders, hook
  contexts (by hook name) and other attachments (by type). hook_success records (a hook's log) and prompt_snapshot
  records (the system prompt and tools) are not items; the snapshot's tokens count as always-visible text for the miss
  count.
- Sizes. Exact: each request's context, its cache read, write (by TTL) and uncached input, its output tokens and, where
  the request's final usage record holds it, its thinking count (usage.output_tokens_details.thinking_tokens: a usage
  number, never a thinking block's field). With --thinking-size exact (the default) a request with that count sizes its
  thinking item exactly and its visible blocks as the exact rest (output minus thinking), split by characters. MODELED,
  otherwise: thinking = output minus the visible characters at 3.0 per token (the audit's low estimate, the brief's
  method; --thinking-size model forces it everywhere) and visible blocks at 3.0 characters per token; user-side content
  always at 2.90 characters per token (the audit's fit, §3.4). Thinking text is never read: only a block's type and
  whether its stored text is empty. Under a policy the active context is the exact context minus the modeled savings.

THE POLICY (`simulate`: a pure function of a timeline and one grid cell B, L, A, rules, mode, turn unit, K).
- R1, superseded copies: a task reminder once a newer one entered; a Read result once the same file_path was Read
  again; a hook context once a newer one from the same hook name entered. R2: thinking. R3: tool results older than A
  requests (age = the request index minus the index of the first request that carried the item; older = age > A).
  R4: tool inputs of more than --large-input tokens, older than A requests.
- Protected, never archived: the segment's first user message, typed user text, loaded skill bodies (every copy; no
  rule targets them), and every item of the current turn and the last K turns (so R2 reaches thinking before those).
- An archived item leaves a stub of --stub-tokens (call id, name, command head, size, pointer: a stub keeps its call
  and result paired); thinking is dropped whole (cost 0), as the design's C2 drops it. An item no larger than its stub
  is never archived.
- Hysteresis: at a check point where the active context passes B, archive in rule order, oldest first, until it is at
  or under L (or nothing more is eligible); then only append until it passes B again. Check points: every request
  (`per-request`) or the first request of each turn (`between-turn`).

THE CACHE MODEL, in base-input-price units, against the real session. Every request after a trim reads the saved
tokens no more: -read x saved. A trim rewrites the prompt from its edit point (the oldest item that trim archived):
the tokens after it that the real request read from the cache become writes, +(write - read) x max(0, tail - real
write - real uncached); the prefix before the edit point comes from the exact context of the request before that item
entered. Real writes are priced by their recorded TTL; extra writes at the run's dominant TTL. CACHE_SOURCE names the
ratios' source; they are parameters.

USE-AFTER-ARCHIVE, per archived item: scripts/jev_pipes/accounting.miss (the committed P1 definition) with the item's
text as the original, its stub as the kept text, and as the history the tokens of the segment's earlier items (P1's
earlier history), of every item still active after the trim, of every stub and of the system prompt snapshot. The
lookahead is the next 20 tool inputs or assistant texts after the trim (20 tool calls for a re-run), and, as the second
horizon, all of them to the end of the segment. The history and the lookahead are passed restricted to the item's own
tokens: miss() computes tokens(original) - tokens(kept) - history, then & used, so a token outside the item's own set
cannot change its answer (tests prove the equality). A visible-only variant drops the earlier-history term, so an
earlier copy that is itself archived no longer hides a token. Thinking is never scored (its text is never read). The
counts are a lower bound on need: a need that leaves no distinctive token or re-run in the record is not seen.

Nothing here prints or stores session text: outputs carry counts, sizes, byte offsets, tool_use ids and tool, hook,
attachment-type and rule names only (a name must match NAME_RE or becomes "<unnamed>").
"""
from __future__ import annotations

import argparse
import bisect
import collections
import datetime
import heapq
import json
import re
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jev_pipes import accounting, transcript  # noqa: E402

USER_CPT = 2.90  # characters per token, user-side content (TRIM-AUDIT §3.4 fit)
ASSISTANT_CPT = 3.0  # characters per token, visible assistant output (TRIM-AUDIT §3 Method, the low thinking estimate)
STUB_TOKENS = 40  # the brief's stub cost
LARGE_INPUT_TOKENS = 500  # R4's "large": set by neither the brief nor the design, so a parameter
K_TURNS = 2  # the design's last K turns
HEAD_CHARS = 80  # a stub's command head
TASK_REMINDER_WRAPPER_CHARS = 420  # a reminder's fixed rendered text (docs/research/findings/jev-pipes/inject_cost.py)
CACHE_READ = 0.05
CACHE_READ_ALT = 0.10
CACHE_WRITE_1H = 2.0
CACHE_WRITE_5M = 1.25
CACHE_SOURCE = ("UNSURE, parameters: the live prompt-caching page was not fetched (the brief's boundary forbids a "
                "network call). Source: the claude-api skill bundled with Claude Code 2.1.283, "
                "shared/prompt-caching.md line 144: cache reads '0.05x on Claude Opus 5.5 ($0.20/MTok)' (every request "
                "here ran claude-opus-5-5), '~0.1x' on other models (the alternative column); writes '1.25x for "
                "5-minute TTL, 2x for 1-hour TTL'.")
BUDGETS = (100_000, 131_072, 150_000, 200_000, 250_000)
LOW_FRACTIONS = {200_000: (0.75, 0.6)}  # every other budget: (0.75,)
AGES = (10, 20, 50)
RULE_SETS = (("R1",), ("R1", "R2"), ("R1", "R2", "R3"), ("R1", "R2", "R3", "R4"))
MODES = ("between-turn", "per-request")
TURN_UNITS = ("stop", "prompt", "request")
THINKING_SIZES = ("exact", "model")
AGE_BUCKETS = (("0-10", 0, 10), ("11-50", 11, 50), ("51-200", 51, 200), ("201+", 201, None))
NAME_RE = re.compile(r"[A-Za-z0-9_:.\-]{1,80}")
USER_SIDE = frozenset({"tool_result", "typed_user_text", "other_user_text", "task_reminder", "hook_context",
                       "other_attachment"})
SKIP_ATTACHMENTS = frozenset({"hook_success", "prompt_snapshot"})
TYPED_ORIGINS = frozenset({"human", "coordinator"})
NOTE_ORIGINS = frozenset({"task-notification", "peer"})
HEAD_KEYS = ("command", "file_path", "notebook_path", "pattern", "path", "skill", "url", "query")
SKIP_KEYS = frozenset({"type", "source", "data", "signature"})


def safe_name(value: object) -> str:
    """A tool, hook or attachment-type name as an output may carry it; anything else is '<unnamed>'."""
    return value if isinstance(value, str) and NAME_RE.fullmatch(value) else "<unnamed>"


def flatten(value: object) -> str:
    """Every string inside a value, in a fixed order (an attachment's text; binary payloads under SKIP_KEYS left out)."""
    out, stack = [], [value]
    while stack:
        v = stack.pop()
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            stack.extend(v[k] for k in sorted(v, reverse=True) if k not in SKIP_KEYS)
        elif isinstance(v, list):
            stack.extend(reversed(v))
    return "\n".join(out)


def stub_text(kind: str, name: str, tool_use_id: str, call_input: object, chars: int, offset: int,
              is_error: bool) -> str:
    """The one-line stub an archived item leaves (in memory only: the miss count's kept text)."""
    head = ""
    if isinstance(call_input, dict):
        for key in HEAD_KEYS:
            if isinstance(call_input.get(key), str):
                head = " ".join(call_input[key].split())[:HEAD_CHARS]
                break
    return f"[archived {kind} {name} id={tool_use_id} head={head} chars={chars} error={is_error} pointer={offset}]"


@dataclass
class Request:
    index: int
    seg: int
    offset: int
    day: str
    time: str
    model: str
    context: int
    read: int
    write: int
    write_1h: int
    write_5m: int
    uncached: int
    raw_stop: int
    raw_prompt: int
    output: int = 0
    turn_stop: int = 0
    turn_prompt: int = 0

    def turn(self, unit: str) -> int:
        return self.index if unit == "request" else (self.turn_stop if unit == "stop" else self.turn_prompt)


@dataclass
class Item:
    offset: int  # byte offset of the record: the pointer
    sub: int
    seg: int
    kind: str
    name: str
    chars: int
    raw_stop: int
    raw_prompt: int
    text: str | None = None  # memory only; None for thinking (never read)
    tool_use_id: str = ""
    key: tuple | None = None  # R1's supersede key
    typed: bool = False
    first_user: bool = False
    skill: str | None = None
    rerun: tuple | None = None
    stub: str = ""
    size: float = 0.0
    req: int = -1  # global index of the first request whose context holds it
    pos: int = -1  # position in its segment
    turn_stop: int = 0
    turn_prompt: int = 0
    toks: frozenset = frozenset()
    stub_toks: frozenset = frozenset()
    prefix_real: float = 0.0  # context tokens before it (the cache model's edit point)

    def turn(self, unit: str) -> int:
        return self.req if unit == "request" else (self.turn_stop if unit == "stop" else self.turn_prompt)


@dataclass
class Segment:
    index: int
    requests: list
    items: list
    fixed: frozenset


@dataclass
class Timeline:
    path: str
    limit: int
    start: int
    sidechain: bool
    requests: list
    segments: list
    boundaries: list  # (offset, day) of each compact_boundary on the thread
    stats: collections.Counter
    params: dict = field(default_factory=dict)


def _request(index, seg, offset, record, message, usage, raw_stop, raw_prompt, stats) -> Request | None:
    parts = [usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")]
    if not all(type(v) is int and v >= 0 for v in parts):  # declared type only; never coerce (AF-AP-72), as the walker
        stats["requests_with_malformed_usage"] += 1
        return None
    split = usage.get("cache_creation") if isinstance(usage.get("cache_creation"), dict) else {}
    w1, w5 = split.get("ephemeral_1h_input_tokens"), split.get("ephemeral_5m_input_tokens")
    if not (type(w1) is int and type(w5) is int and w1 >= 0 and w5 >= 0 and w1 + w5 == parts[1]):
        stats["requests_without_a_ttl_split"] += 1
        w1, w5 = parts[1], 0
    stamp = record.get("timestamp") if isinstance(record.get("timestamp"), str) else ""
    return Request(index, seg, offset, stamp[:10] or "unknown", stamp, safe_name(message.get("model")), sum(parts),
                   parts[2], parts[1], w1, w5, parts[0], raw_stop, raw_prompt)


def _user_kind(record: dict, skill_calls: dict) -> tuple[str, str, bool, str | None]:
    origin = record.get("origin")
    okind = origin.get("kind") if isinstance(origin, dict) else None
    if record.get("isCompactSummary") is True:
        return "other_user_text", "compact_summary", False, None
    if okind in TYPED_ORIGINS:
        return "typed_user_text", okind, True, None
    if okind in NOTE_ORIGINS:
        return "other_user_text", okind, False, None
    if record.get("isMeta") is True:
        source = record.get("sourceToolUseID")
        if isinstance(source, str) and source in skill_calls:
            return "other_user_text", "skill_body", False, skill_calls[source]
        return "other_user_text", "meta", False, None
    return "typed_user_text", "no_origin", True, None


def _attachment(attachment: dict) -> tuple[str, str, str, int, tuple | None, bool]:
    """(kind, name, text, characters, R1 key, typed) of one attachment."""
    atype = attachment.get("type")
    if atype == "task_reminder":
        rows = attachment.get("content") if isinstance(attachment.get("content"), list) else []
        text = "".join("#%s. [%s] %s\n" % (r.get("id"), r.get("status"), r.get("subject")) for r in rows
                       if isinstance(r, dict))
        return "task_reminder", "task_reminder", text, TASK_REMINDER_WRAPPER_CHARS + len(text), ("task_reminder",), False
    if atype == "hook_additional_context":
        content = attachment.get("content")
        text = ("\n".join(c for c in content if isinstance(c, str)) if isinstance(content, list)
                else content if isinstance(content, str) else "")
        hook = safe_name(attachment.get("hookName"))
        return "hook_context", hook, text, len(text), ("hook", hook), False
    if atype == "queued_command":
        text = flatten(attachment.get("prompt"))
        if attachment.get("commandMode") == "prompt":
            return "typed_user_text", "queued_prompt", text, len(text), None, True
        return "other_attachment", "queued_command", text, len(text), None, False
    text = flatten(attachment)
    return "other_attachment", safe_name(atype), text, len(text), None, False


def build(path: str, limit: int, *, start: int = 0, sidechain: bool = False, user_cpt: float = USER_CPT,
          assistant_cpt: float = ASSISTANT_CPT, thinking_size: str = "exact", with_items: bool = True) -> Timeline:
    """One pass over the records before `limit` from `start`: requests, segments, turns and (with_items) the items."""
    if thinking_size not in THINKING_SIZES:
        raise ValueError(f"thinking_size must be one of {THINKING_SIZES}")
    stats: collections.Counter = collections.Counter()
    requests: list[Request] = []
    boundaries: list[tuple[int, str]] = []
    items: list[Item] = []
    by_rid: dict[str, Request] = {}
    seen: set[str] = set()
    out_max: dict[str, int] = {}
    exact_thinking: dict[str, int] = {}
    visible: dict[str, list] = collections.defaultdict(list)
    thinking: dict[str, list] = {}
    calls: dict[str, tuple] = {}
    skill_calls: dict[str, str] = {}
    fixed: dict[int, set] = collections.defaultdict(set)
    seg = raw_stop = raw_prompt = 0
    last_pid, first_user_open = None, True
    for offset, record in transcript.iter_records(path, limit, stats):
        if offset < start:
            continue
        side = record.get("isSidechain")
        if isinstance(side, bool) and side is not sidechain:
            stats["records_on_the_other_thread"] += 1
            continue
        kind = record.get("type")
        if kind == "system":
            if record.get("subtype") == "compact_boundary":
                seg, raw_stop, raw_prompt, first_user_open = seg + 1, raw_stop + 1, raw_prompt + 1, True
                stamp = record.get("timestamp") if isinstance(record.get("timestamp"), str) else ""
                boundaries.append((offset, stamp[:10] or "unknown"))
            elif record.get("subtype") == "stop_hook_summary":
                raw_stop += 1
                stats["stop_hook_summaries"] += 1
            continue
        if kind == "assistant":
            message = record.get("message") if isinstance(record.get("message"), dict) else {}
            if message.get("model") == "<synthetic>":
                stats["synthetic_records_excluded"] += 1
                continue
            rid = record.get("requestId") if isinstance(record.get("requestId"), str) else ""
            usage = message.get("usage")
            if rid and isinstance(usage, dict):
                out = usage.get("output_tokens")
                if type(out) is int and out >= 0:
                    out_max[rid] = max(out_max.get(rid, 0), out)
                details = usage.get("output_tokens_details")  # a usage count, not a thinking block's field
                count = details.get("thinking_tokens") if isinstance(details, dict) else None
                if type(count) is int and count >= 0:
                    exact_thinking[rid] = max(exact_thinking.get(rid, 0), count)
                if rid not in seen:  # the first record with usage defines the request, as the committed walker
                    seen.add(rid)
                    request = _request(len(requests), seg, offset, record, message, usage, raw_stop, raw_prompt, stats)
                    if request is not None:
                        requests.append(request)
                        by_rid[rid] = request
            elif rid:
                stats["assistant_records_without_usage"] += 1
            if with_items:
                _assistant_blocks(record, offset, seg, rid, raw_stop, raw_prompt, items, visible, thinking, calls,
                                  skill_calls)
            continue
        if kind == "user":
            pid = record.get("promptId")
            if isinstance(pid, str) and pid and pid != last_pid:
                raw_prompt, last_pid = raw_prompt + 1, pid
            if with_items:
                blocks = transcript._blocks(record)
                for sub, block in enumerate(blocks):
                    if block.get("type") == "tool_result":
                        items.append(_result_item(block, offset, sub, seg, raw_stop, raw_prompt, calls, stats))
                text = "\n".join(b["text"] for b in blocks
                                 if b.get("type") == "text" and isinstance(b.get("text"), str) and b["text"])
                if text:
                    ukind, name, typed, skill = _user_kind(record, skill_calls)
                    items.append(Item(offset, len(blocks), seg, ukind, name, len(text), raw_stop, raw_prompt, text=text,
                                      typed=typed, first_user=first_user_open, skill=skill,
                                      stub=stub_text(ukind, name, "", None, len(text), offset, False)))
                    first_user_open = False
            continue
        if kind == "attachment":
            attachment = record.get("attachment")
            if not isinstance(attachment, dict):
                stats["attachment_records_without_a_body"] += 1
                continue
            if attachment.get("type") == "prompt_snapshot":
                if with_items:
                    fixed[seg].update(accounting.tokens(flatten(attachment)))
                continue
            if attachment.get("type") in SKIP_ATTACHMENTS or not with_items:
                continue
            akind, name, text, chars, key, typed = _attachment(attachment)
            items.append(Item(offset, 0, seg, akind, name, chars, raw_stop, raw_prompt, text=text, key=key, typed=typed,
                              stub=stub_text(akind, name, "", None, chars, offset, False)))
            continue
        stats["bookkeeping_records"] += 1
    for rid, request in by_rid.items():
        request.output = out_max.get(rid, 0)
    for item in items:  # modeled sizes; the exact path below overrides a request's visible blocks
        item.size = item.chars / (user_cpt if item.kind in USER_SIDE else assistant_cpt)
    check = {"requests_with_both": 0, "exact_thinking_tokens": 0, "modeled_thinking_tokens": 0.0}
    for rid in sorted(set(visible) | set(thinking)):
        request = by_rid.get(rid)
        chars = sum(it.chars for it in visible.get(rid, ()))
        modeled = max(0.0, request.output - chars / assistant_cpt) if request is not None else 0.0
        exact = exact_thinking.get(rid) if request is not None else None
        if exact is not None and rid in thinking:
            check["requests_with_both"] += 1
            check["exact_thinking_tokens"] += exact
            check["modeled_thinking_tokens"] += modeled
        if thinking_size == "exact" and exact is not None:
            rest = max(0.0, request.output - exact)  # the visible output, exactly; split by characters
            for it in visible.get(rid, ()):
                it.size = rest * it.chars / chars if chars else 0.0
            think, how = float(exact), "exact"
        else:
            think, how = modeled, "model"
        if request is not None and chars > 0:
            stats[f"visible_output_sized_{how}"] += 1
        if rid in thinking:
            offset, sub, seg_of, rs, rp, blocks, empty = thinking[rid]
            stats["thinking_blocks"] += blocks
            stats["thinking_blocks_stored_empty"] += empty
            item = Item(offset, sub, seg_of, "thinking", "thinking", 0, rs, rp)
            if request is None:
                stats["thinking_without_a_request"] += 1
            else:
                item.size = think
                stats[f"thinking_sized_{how}"] += 1
            items.append(item)
    check["modeled_thinking_tokens"] = round(check["modeled_thinking_tokens"], 1)
    segments = _segments(requests, items, fixed, stats)
    _turns(requests, segments)
    if with_items:
        for segment in segments:
            _finish(segment)
    stats["requests"] = len(requests)
    stats["segments"] = len(segments)
    return Timeline(path, limit, start, sidechain, requests, segments, boundaries, stats,
                    {"user_cpt": user_cpt, "assistant_cpt": assistant_cpt, "thinking_size": thinking_size,
                     "thinking_check": check})


def _assistant_blocks(record, offset, seg, rid, raw_stop, raw_prompt, items, visible, thinking, calls, skill_calls):
    for sub, block in enumerate(transcript._blocks(record)):
        btype = block.get("type")
        if btype in ("thinking", "redacted_thinking"):
            # A thinking block's text is never read: only its type and whether its stored text is empty.
            entry = thinking.setdefault(rid or f"@{offset}", [offset, sub, seg, raw_stop, raw_prompt, 0, 0])
            entry[5] += 1
            if btype == "thinking" and block.get("thinking") == "":
                entry[6] += 1
        elif btype == "text" and isinstance(block.get("text"), str) and block["text"]:
            item = Item(offset, sub, seg, "assistant_text", "assistant_text", len(block["text"]), raw_stop, raw_prompt,
                        text=block["text"],
                        stub=stub_text("assistant_text", "text", "", None, len(block["text"]), offset, False))
            items.append(item)
            visible[rid].append(item)
        elif btype == "tool_use":
            name = block.get("name") if isinstance(block.get("name"), str) else "?"
            call_input = block.get("input")
            body = json.dumps(call_input, ensure_ascii=False)  # as the committed walker tokenizes a tool input
            tool_use_id = block.get("id") if isinstance(block.get("id"), str) else ""
            calls[tool_use_id] = (name, call_input)
            if name == "Skill" and isinstance(call_input, dict) and isinstance(call_input.get("skill"), str):
                skill_calls[tool_use_id] = call_input["skill"]
            item = Item(offset, sub, seg, "tool_input", safe_name(name), len(body), raw_stop, raw_prompt, text=body,
                        tool_use_id=tool_use_id, rerun=transcript.rerun_key(name, call_input),
                        stub=stub_text("tool_input", safe_name(name), tool_use_id, call_input, len(body), offset, False))
            items.append(item)
            visible[rid].append(item)


def _result_item(block, offset, sub, seg, raw_stop, raw_prompt, calls, stats) -> Item:
    tool_use_id = block.get("tool_use_id") if isinstance(block.get("tool_use_id"), str) else ""
    if tool_use_id not in calls:
        stats["results_without_a_known_call"] += 1
    name, call_input = calls.get(tool_use_id, ("?", None))
    text = transcript.result_text(block)
    key = None
    if name == "Read" and isinstance(call_input, dict) and isinstance(call_input.get("file_path"), str):
        key = ("Read", call_input["file_path"])
    return Item(offset, sub, seg, "tool_result", safe_name(name), len(text), raw_stop, raw_prompt, text=text,
                tool_use_id=tool_use_id, key=key, rerun=transcript.rerun_key(name, call_input),
                stub=stub_text("tool_result", safe_name(name), tool_use_id, call_input, len(text), offset,
                               block.get("is_error") is True))


def _segments(requests, items, fixed, stats) -> list[Segment]:
    by_req, by_items = collections.defaultdict(list), collections.defaultdict(list)
    for request in requests:
        by_req[request.seg].append(request)
    for item in items:
        by_items[item.seg].append(item)
    segments = []
    for seg in sorted(by_req):
        reqs = by_req[seg]
        offsets = [r.offset for r in reqs]
        kept = []
        for item in sorted(by_items.get(seg, ()), key=lambda it: (it.offset, it.sub)):
            j = bisect.bisect_right(offsets, item.offset)
            if j == len(reqs):
                stats["items_after_their_segments_last_request"] += 1
                continue
            item.req, item.pos = reqs[j].index, len(kept)
            kept.append(item)
        segments.append(Segment(seg, reqs, kept, frozenset(fixed.get(seg, ()))))
    stats["items_in_segments_without_a_request"] += sum(len(v) for s, v in by_items.items() if s not in by_req)
    return segments


def _turns(requests, segments) -> None:
    """Dense turn ids: only turns that hold a request count; an item in an empty turn joins the next turn."""
    for unit in ("stop", "prompt"):
        values = sorted({getattr(r, "raw_" + unit) for r in requests})
        for request in requests:
            setattr(request, "turn_" + unit, bisect.bisect_left(values, getattr(request, "raw_" + unit)))
        for segment in segments:
            for item in segment.items:
                setattr(item, "turn_" + unit, bisect.bisect_left(values, getattr(item, "raw_" + unit)))


def _finish(segment: Segment) -> None:
    """Tokens (accounting.tokens, the committed classes) and each item's context prefix for the cache model."""
    for item in segment.items:
        if item.text is not None:
            item.toks = accounting.tokens(item.text)
            item.stub_toks = accounting.tokens(item.stub)
    first = segment.requests[0].index
    context = {r.index: r.context for r in segment.requests}
    groups = collections.defaultdict(list)
    for item in segment.items:
        groups[item.req].append(item)
    for req, group in groups.items():
        if req == first:  # entered before the segment's first request: its context minus the modeled tail
            tail = 0.0
            for item in reversed(group):
                tail += item.size
                item.prefix_real = max(0.0, context[first] - tail)
        else:
            acc = float(context[req - 1])
            for item in group:
                item.prefix_real = acc
                acc += item.size


class Index:
    """What the simulation and the miss count read about one segment, independent of the grid cell."""

    def __init__(self, segment: Segment, stub_tokens: float, large_input_tokens: float):
        items = segment.items
        self.segment = segment
        self.req = [it.req for it in items]
        self.r2 = [it.pos for it in items if it.kind == "thinking" and it.size > 0]
        self.r3 = [it.pos for it in items if it.kind == "tool_result" and it.size > stub_tokens]
        self.r4 = [it.pos for it in items if it.kind == "tool_input" and it.size > max(large_input_tokens, stub_tokens)]
        self.supersedes: list = [None] * len(items)
        newest: dict = {}
        for it in items:
            if it.key is not None:
                self.supersedes[it.pos] = newest.get(it.key)  # the copy this one supersedes: the previous newest
                newest[it.key] = it.pos
        self.turns = {unit: [it.turn(unit) for it in items] for unit in TURN_UNITS}
        look = [it for it in items if it.kind in ("tool_input", "assistant_text")]
        self.la_req = [it.req for it in look]
        call_items = [it for it in look if it.kind == "tool_input"]
        self.call_req = [it.req for it in call_items]
        self.call_keys = [it.rerun for it in call_items]
        self.last_call = {key: i for i, key in enumerate(self.call_keys)}
        self.tok_la: dict = collections.defaultdict(list)
        for i, it in enumerate(look):
            for t in it.toks:
                self.tok_la[t].append(i)
        self.tok_items: dict = collections.defaultdict(list)
        self.first_occ: dict = {}
        for it in items:
            for t in it.toks:
                self.tok_items[t].append(it.pos)
                self.first_occ.setdefault(t, it.pos)
        self.memo: dict = {}  # exact memo of accounting.miss, shared by every cell of a run (see miss_memo)
        self.memo_calls = 0


def miss_memo(ix: Index, item: Item, history: frozenset, used: frozenset, calls: list) -> tuple[int, bool]:
    """accounting.miss(item.text, item.stub, history, [used], calls, item.rerun), memoized exactly: miss() returns
    (|(tokens(original) - tokens(kept) - history) & used|, rerun_key in calls), and tokens(original) is item.toks, so its
    answer depends on history only through item.toks - history, on used only through that set's intersection with
    used, and on calls only through membership. Every distinct case is still computed by the committed function."""
    base = item.toks - history
    key = (item.pos, base, base & used, item.rerun is not None and item.rerun in calls)
    hit = ix.memo.get(key)
    if hit is None:
        hit = accounting.miss(item.text, item.stub, history, [used], calls, item.rerun)
        ix.memo[key] = hit
        ix.memo_calls += 1
    return hit


class Fenwick:
    def __init__(self, n: int):
        self.tree = [0.0] * (n + 1)

    def add(self, i: int, value: float) -> None:
        i += 1
        while i < len(self.tree):
            self.tree[i] += value
            i += i & -i

    def prefix(self, i: int) -> float:
        """The sum over positions [0, i)."""
        total = 0.0
        while i > 0:
            total += self.tree[i]
            i -= i & -i
        return total


@dataclass(frozen=True)
class Cell:
    budget: int
    low: int
    age: int
    rules: tuple
    mode: str
    unit: str = "stop"
    k: int = K_TURNS


def indexes(tl: Timeline, stub_tokens: float = STUB_TOKENS, large_input_tokens: float = LARGE_INPUT_TOKENS) -> dict:
    return {s.index: Index(s, stub_tokens, large_input_tokens) for s in tl.segments}


def _protected_kind(item: Item) -> bool:
    return item.typed or item.first_user or item.skill is not None or item.name == "skill_body"


def simulate(tl: Timeline, cell: Cell, idx: dict, *, stub_tokens: float = STUB_TOKENS, keep_map: bool = False) -> dict:
    """The policy over every segment: per-request active context, the trims, the use-after-archive rows, the cache
    terms and (keep_map) the archive map {(segment, position): (rule, trim number, request index, stub cost)}."""
    out = {"active": [], "trims": [], "uaa": [], "archive": {}, "saved": []}
    for segment in tl.segments:
        _simulate_segment(segment, idx[segment.index], cell, stub_tokens, out, keep_map)
    return out


def _simulate_segment(segment: Segment, ix: Index, cell: Cell, stub_tokens: float, out: dict, keep_map: bool) -> None:
    items = segment.items
    n = len(items)
    turn = ix.turns[cell.unit]
    archived: list = [None] * n
    bit = Fenwick(n)
    heap: list = []
    lists = {"R2": ix.r2, "R3": ix.r3, "R4": ix.r4}
    ptr = {"R2": 0, "R3": 0, "R4": 0}
    stubs: collections.Counter = collections.Counter()
    saved = 0.0
    entered = 0
    trims_here = 0
    prev_turn = None
    for j, request in enumerate(segment.requests):
        r = request.index
        while entered < n and items[entered].req <= r:
            older = ix.supersedes[entered]
            if older is not None and archived[older] is None:
                heapq.heappush(heap, older)  # the older copy is superseded once the newer one entered
            entered += 1
        cur = request.turn(cell.unit)
        turn_start = j == 0 or cur != prev_turn
        prev_turn = cur
        protect_from = bisect.bisect_left(turn, cur - cell.k, 0, entered)  # the current turn and the last K turns
        active = request.context - saved
        newly: list[int] = []

        def archive(q: int, rule: str) -> float:
            nonlocal saved
            item = items[q]
            stub = 0.0 if item.kind == "thinking" else stub_tokens  # thinking is dropped whole; the rest leave a stub
            gain = item.size - stub
            if gain <= 0 or _protected_kind(item):
                return 0.0
            archived[q] = (rule, trims_here, r, stub)
            bit.add(q, gain)
            saved += gain
            newly.append(q)
            if stub:
                stubs.update(item.stub_toks)
            return gain

        target = cell.low  # hysteresis: once past B, archive down to L
        if (cell.mode == "per-request" or turn_start) and active > cell.budget:
            for rule in cell.rules:
                if rule == "R1":
                    while heap and active > target:
                        q = heap[0]
                        if q >= protect_from:
                            break
                        heapq.heappop(heap)
                        if archived[q] is None:
                            active -= archive(q, "R1")
                    continue
                lst = lists[rule]
                while ptr[rule] < len(lst) and active > target:
                    q = lst[ptr[rule]]
                    if q >= protect_from:
                        break
                    if rule != "R2" and not items[q].req < r - cell.age:  # R3/R4: older than A requests
                        break
                    ptr[rule] += 1
                    if archived[q] is None:
                        active -= archive(q, rule)
        trim = None
        if newly:
            edit = min(newly)
            prefix = max(0.0, items[edit].prefix_real - bit.prefix(edit))  # earlier trims' savings before the edit
            sent = request.context - saved
            tail = max(0.0, sent - prefix)
            trim = {"request": r, "offset": request.offset, "segment": segment.index, "items": len(newly),
                    "archived_tokens": sum(items[q].size for q in newly),
                    "saved_tokens": sum(items[q].size - archived[q][3] for q in newly),
                    "edit_offset": items[edit].offset, "tail_tokens": tail,
                    "extra_write_tokens": max(0.0, tail - request.write - request.uncached),
                    "turn_start": turn_start}
            vis: dict = {}
            for q in newly:
                out["uaa"].append(_uaa(ix, items, q, r, archived, stubs, entered, vis, segment.fixed))
                if keep_map:
                    out["archive"][(segment.index, q)] = archived[q]
            trims_here += 1
            out["trims"].append(trim)
        out["active"].append((r, request.context - saved))
        out["saved"].append(saved)


def active_list(segment: Segment, archive: dict, request_index: int) -> list[tuple[int, str]]:
    """The design's active list at one request: (position, 'kept' | 'stub' | 'dropped') for every item in its context,
    read from simulate(..., keep_map=True)'s archive map (an item archived at or before that request is a stub, or
    dropped when it left none)."""
    out = []
    for it in segment.items:
        if it.req > request_index:
            break
        mark = archive.get((segment.index, it.pos))
        if mark is None or mark[2] > request_index:
            out.append((it.pos, "kept"))
        else:
            out.append((it.pos, "stub" if mark[3] else "dropped"))
    return out


def _visible(t: str, ix: Index, archived: list, stubs: collections.Counter, entered: int, cache: dict) -> bool:
    """Is token t in a stub or in an item that entered and is not archived (after the current trim)?"""
    hit = cache.get(t)
    if hit is None:
        hit = stubs[t] > 0
        if not hit:
            positions = ix.tok_items.get(t, ())
            for i in range(bisect.bisect_left(positions, entered) - 1, -1, -1):
                if archived[positions[i]] is None:
                    hit = True
                    break
        cache[t] = hit
    return hit


def _uaa(ix: Index, items: list, q: int, r: int, archived: list, stubs, entered: int, cache: dict,
         fixed: frozenset) -> dict:
    item = items[q]
    rule = archived[q][0]
    row = {"rule": rule, "tool": item.name if item.kind in ("tool_result", "tool_input") else item.kind,
           "age": r - item.req, "scored": item.kind != "thinking"}
    if not row["scored"]:  # thinking: its text is never read, so it is never scored
        return row
    kept = frozenset(t for t in item.toks if t in fixed or _visible(t, ix, archived, stubs, entered, cache))
    earlier = kept | frozenset(t for t in item.toks if ix.first_occ[t] < q)  # P1's earlier history, and the kept text
    visible_only = kept
    start = bisect.bisect_right(ix.la_req, r)  # the first tool input or assistant text produced after the trim
    used20, used_h = set(), set()
    for t in item.toks:
        uses = ix.tok_la.get(t)
        if uses and uses[-1] >= start:
            used_h.add(t)
            i = bisect.bisect_left(uses, start)
            if uses[i] < start + accounting.LOOKAHEAD:
                used20.add(t)
    call_start = bisect.bisect_right(ix.call_req, r)
    calls20 = ix.call_keys[call_start:call_start + accounting.LOOKAHEAD]
    calls_h = [item.rerun] if item.rerun is not None and ix.last_call.get(item.rerun, -1) >= call_start else []
    for label, history in (("", earlier), ("visible_", visible_only)):
        hits20, rerun20 = miss_memo(ix, item, history, frozenset(used20), calls20)
        hits_h, rerun_h = miss_memo(ix, item, history, frozenset(used_h), calls_h)
        row[label + "m20"] = hits20 > 0 or rerun20
        row[label + "mh"] = hits_h > 0 or rerun_h
        row[label + "hits20"] = hits20
    return row


def floors(tl: Timeline, idx: dict, unit: str, k: int = K_TURNS) -> list[tuple[int, float, float]]:
    """(request index, the protected set alone, the segment start alone) per request: the segment's first context plus
    the modeled size of every protected item that entered after it (typed text, the newest copy of each skill body,
    the current turn and the last K turns)."""
    rows = []
    for segment in tl.segments:
        items = segment.items
        turn = idx[segment.index].turns[unit]
        first = segment.requests[0]
        size_all, size_typed = [0.0], [0.0]
        for it in items:
            late = it.req > first.index
            size_all.append(size_all[-1] + (it.size if late else 0.0))
            size_typed.append(size_typed[-1] + (it.size if late and (it.typed or it.first_user) else 0.0))
        newest_skill: dict = {}
        entered = 0
        for request in segment.requests:
            while entered < len(items) and items[entered].req <= request.index:
                if items[entered].skill is not None:
                    newest_skill[items[entered].skill] = entered
                entered += 1
            protect_from = bisect.bisect_left(turn, request.turn(unit) - k, 0, entered)
            skills = sum(items[p].size for p in newest_skill.values()
                         if p < protect_from and items[p].req > first.index and not items[p].typed)
            value = (first.context + size_all[entered] - size_all[protect_from] + size_typed[protect_from] + skills)
            rows.append((request.index, value, float(first.context)))
    return rows


def grid(modes=MODES, units=("stop",)) -> list[Cell]:
    cells = []
    for unit in units:
        for budget in BUDGETS:
            for fraction in LOW_FRACTIONS.get(budget, (0.75,)):
                for rules in RULE_SETS:
                    for age in AGES:
                        for mode in modes:
                            cells.append(Cell(budget, round(budget * fraction), age, rules, mode, unit))
    return cells


def _stat(values: list) -> dict:
    if not values:
        return {"n": 0, "median": None, "p90": None, "max": None, "min": None, "sum": 0}
    return {"n": len(values), "median": round(float(statistics.median(values)), 1),
            "p90": round(float(accounting.percentile(values, 90)), 1), "max": round(float(max(values)), 1),
            "min": round(float(min(values)), 1), "sum": round(float(sum(values)), 1)}


def _bucket(age: int) -> str:
    for label, lo, hi in AGE_BUCKETS:
        if age >= lo and (hi is None or age <= hi):
            return label
    return "?"


def uaa_summary(rows: list[dict]) -> dict:
    scored = [r for r in rows if r["scored"]]
    out = {"archived_items": len(rows), "scored_items": len(scored), "thinking_not_scored": len(rows) - len(scored)}
    for key, label in (("m20", "at20"), ("mh", "at_horizon"), ("visible_m20", "visible_only_at20"),
                       ("visible_mh", "visible_only_at_horizon")):
        hit = [r for r in scored if r[key]]
        out[label] = {"items": len(hit),
                      "by_rule": dict(sorted(collections.Counter(r["rule"] for r in hit).items())),
                      "by_tool": dict(sorted(collections.Counter(r["tool"] for r in hit).items())),
                      "by_age": dict(sorted(collections.Counter(_bucket(r["age"]) for r in hit).items()))}
    out["scored_by_rule"] = dict(sorted(collections.Counter(r["rule"] for r in scored).items()))
    out["scored_by_tool"] = dict(sorted(collections.Counter(r["tool"] for r in scored).items()))
    out["scored_by_age"] = dict(sorted(collections.Counter(_bucket(r["age"]) for r in scored).items()))
    return out


def cache_terms(tl: Timeline, sim: dict, read: float, extra_ratio: float) -> dict:
    real = sum(read * q.read + CACHE_WRITE_5M * q.write_5m + CACHE_WRITE_1H * q.write_1h + q.uncached
               for q in tl.requests)
    saved_read = read * sum(sim["saved"])
    extra = (extra_ratio - read) * sum(t["extra_write_tokens"] for t in sim["trims"])
    net = extra - saved_read
    return {"read_ratio": read, "extra_write_ratio": extra_ratio, "real_units": round(real, 1),
            "read_saving_units": round(saved_read, 1), "extra_write_units": round(extra, 1),
            "net_units": round(net, 1), "net_share_of_real": round(net / real, 6) if real else None}


def summarize_cell(tl: Timeline, cell: Cell, sim: dict, floor_rows: list, extra_ratio: float) -> dict:
    active = [a for _, a in sim["active"]]
    trims = sim["trims"]
    gaps, last = [], {}
    for t in trims:
        if t["segment"] in last:
            gaps.append(t["request"] - last[t["segment"]])
        last[t["segment"]] = t["request"]
    archived_rules = collections.Counter(r["rule"] for r in sim["uaa"])
    return {
        "B": cell.budget, "L": cell.low, "A": cell.age, "rules": "+".join(cell.rules), "mode": cell.mode,
        "turn_unit": cell.unit, "K": cell.k, "a_invariant": not ({"R3", "R4"} & set(cell.rules)),
        "requests": len(active),
        "active": {**{k: v for k, v in _stat(active).items() if k in ("median", "p90", "max")},
                   "over_B": sum(1 for a in active if a > cell.budget)},
        "floor": {"segment_start_over_B": sum(1 for _, _, s in floor_rows if s > cell.budget),
                  "protected_over_B": sum(1 for _, f, _ in floor_rows if f > cell.budget),
                  "protected_over_B_share": round(sum(1 for _, f, _ in floor_rows if f > cell.budget)
                                                  / len(floor_rows), 4) if floor_rows else None},
        "trims": {"count": len(trims), "saved_tokens_per_trim": _stat([t["saved_tokens"] for t in trims]),
                  "archived_tokens_per_trim": _stat([t["archived_tokens"] for t in trims]),
                  "items_per_trim": _stat([t["items"] for t in trims]), "requests_between_trims": _stat(gaps),
                  "rewrite_tokens_per_trim": _stat([t["tail_tokens"] for t in trims]),
                  "at_a_request_that_does_not_start_a_turn": sum(1 for t in trims if not t["turn_start"])},
        "archived_items_by_rule": dict(sorted(archived_rules.items())),
        "cache": cache_terms(tl, sim, CACHE_READ, extra_ratio),
        "cache_at_read_0_1": cache_terms(tl, sim, CACHE_READ_ALT, extra_ratio),
        "use_after_archive": uaa_summary(sim["uaa"]),
    }


FIT_GROUPS = (("tool_results", ("tool_result",)), ("hook_contexts_and_task_reminders", ("hook_context", "task_reminder")),
              ("user_text", ("typed_user_text", "other_user_text")), ("other_attachments", ("other_attachment",)))


def _lstsq(rows: list[list[float]], y: list[float]) -> tuple[list[float], float] | None:
    """Least squares by the normal equations, Gauss-Jordan with pivoting (a handful of columns); None if singular."""
    k = len(rows[0])
    a = [[sum(r[i] * r[j] for r in rows) for j in range(k)] for i in range(k)]
    b = [sum(r[i] * v for r, v in zip(rows, y)) for i in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda i: abs(a[i][c]))
        if abs(a[p][c]) < 1e-9:
            return None
        a[c], a[p], b[c], b[p] = a[p], a[c], b[p], b[c]
        for i in range(k):
            if i != c:
                f = a[i][c] / a[c][c]
                a[i] = [x - f * z for x, z in zip(a[i], a[c])]
                b[i] -= f * b[c]
    coef = [b[i] / a[i][i] for i in range(k)]
    mean = sum(y) / len(y)
    total = sum((v - mean) ** 2 for v in y)
    resid = sum((v - sum(c * x for c, x in zip(coef, r))) ** 2 for r, v in zip(rows, y))
    return coef, (1 - resid / total) if total else 0.0


def calibration_fit(tl: Timeline) -> dict:
    """(context(r) - context(r-1) - output(r-1)) = a + sum over kinds of b_k x characters_k entering before r: the
    characters per token each kind shows against the exact growth (the audit fit one ratio for all kinds, §3.4)."""
    rows, y = [], []
    for segment in tl.segments:
        chars: dict = collections.defaultdict(collections.Counter)
        for it in segment.items:
            for group, kinds in FIT_GROUPS:
                if it.kind in kinds:
                    chars[it.req][group] += it.chars
        for prev, cur in zip(segment.requests, segment.requests[1:]):
            rows.append([1.0] + [float(chars[cur.index][g]) for g, _ in FIT_GROUPS])
            y.append(float(cur.context - prev.context - prev.output))
    used = [i for i in range(1, len(FIT_GROUPS) + 1) if any(r[i] for r in rows)]
    if len(rows) < 20 or not used:
        return {"pairs": len(rows), "fit": None}
    fit = _lstsq([[r[0]] + [r[i] for i in used] for r in rows], y)
    if fit is None:
        return {"pairs": len(rows), "fit": None}
    coef, r2 = fit
    return {"pairs": len(rows), "intercept": round(coef[0], 1), "r2": round(r2, 3),
            "chars_per_token": {FIT_GROUPS[i - 1][0]: (round(1 / c, 2) if c > 0 else None)
                                for i, c in zip(used, coef[1:])}}


def timeline_summary(tl: Timeline) -> dict:
    kinds: dict = collections.defaultdict(lambda: {"items": 0, "tokens": 0.0})
    tools: dict = collections.defaultdict(lambda: {"items": 0, "tokens": 0.0})
    for segment in tl.segments:
        for it in segment.items:
            kinds[it.kind]["items"] += 1
            kinds[it.kind]["tokens"] += it.size
            if it.kind in ("tool_result", "tool_input"):
                tools[it.kind + ":" + it.name]["items"] += 1
                tools[it.kind + ":" + it.name]["tokens"] += it.size
    residual, modeled, diffs = 0, 0.0, []
    for segment in tl.segments:
        user_side = collections.Counter()
        for it in segment.items:
            if it.kind in USER_SIDE:
                user_side[it.req] += it.size
        for prev, cur in zip(segment.requests, segment.requests[1:]):
            exact = cur.context - prev.context - prev.output
            residual += exact
            modeled += user_side[cur.index]
            diffs.append(exact - user_side[cur.index])
    per_turn = {}
    for unit in ("stop", "prompt"):
        counts = collections.Counter((q.seg, q.turn(unit)) for q in tl.requests)
        per_turn[unit] = {"turns": len(counts), "requests_per_turn": _stat(list(counts.values()))}
    return {
        "requests": len(tl.requests), "segments": len(tl.segments),
        "requests_by_model": dict(sorted(collections.Counter(q.model for q in tl.requests).items())),
        "requests_by_day": dict(sorted(collections.Counter(q.day for q in tl.requests).items())),
        "context": _stat([q.context for q in tl.requests]),
        "segment_starts": [{"segment": s.index, "first_offset": s.requests[0].offset, "requests": len(s.requests),
                            "first_context": s.requests[0].context, "items": len(s.items)} for s in tl.segments],
        "turns": per_turn,
        "items_by_kind": {k: {"items": v["items"], "tokens": round(v["tokens"], 1)} for k, v in sorted(kinds.items())},
        "items_by_tool_top20": {k: {"items": v["items"], "tokens": round(v["tokens"], 1)}
                                for k, v in sorted(tools.items(), key=lambda kv: -kv[1]["tokens"])[:20]},
        "calibration": {"pairs": len(diffs), "exact_user_side_residual_sum": residual,
                        "modeled_user_side_sum": round(modeled, 1),
                        "residual_minus_modeled_per_request": _stat(diffs),
                        "per_kind_fit": calibration_fit(tl),
                        "note": "exact residual = context(r) - context(r-1) - output(r-1); the audit's fit gives "
                                "223.9 + user-side characters / 2.90 per request (TRIM-AUDIT §3.4)"},
        "thinking_check": tl.params.get("thinking_check"),
        "write_tokens": {"ttl_1h": sum(q.write_1h for q in tl.requests), "ttl_5m": sum(q.write_5m for q in tl.requests)},
        "stats": dict(sorted(tl.stats.items())),
    }


def run(tl: Timeline, cells: list[Cell], *, stub_tokens: float = STUB_TOKENS,
        large_input_tokens: float = LARGE_INPUT_TOKENS, progress=None) -> tuple[list[dict], dict]:
    idx = indexes(tl, stub_tokens, large_input_tokens)
    w1 = sum(q.write_1h for q in tl.requests)
    w5 = sum(q.write_5m for q in tl.requests)
    extra_ratio = CACHE_WRITE_1H if w1 >= w5 else CACHE_WRITE_5M
    floor_cache: dict = {}
    done: dict = {}
    results = []
    for number, cell in enumerate(cells):
        key = cell if {"R3", "R4"} & set(cell.rules) else Cell(cell.budget, cell.low, AGES[0], cell.rules, cell.mode,
                                                                   cell.unit, cell.k)
        if key not in done:
            if (cell.unit, cell.k) not in floor_cache:
                floor_cache[(cell.unit, cell.k)] = floors(tl, idx, cell.unit, cell.k)
            sim = simulate(tl, key, idx, stub_tokens=stub_tokens)
            done[key] = summarize_cell(tl, key, sim, floor_cache[(cell.unit, cell.k)], extra_ratio)
        row = dict(done[key])
        row["A"] = cell.age
        results.append(row)
        if progress:
            progress(number + 1, len(cells))
    return results, {"extra_write_ratio": extra_ratio, "write_tokens_1h": w1, "write_tokens_5m": w5,
                     "distinct_miss_calls": sum(ix.memo_calls for ix in idx.values()), "distinct_cells": len(done)}


def baseline(tl: Timeline) -> dict:
    contexts = [q.context for q in tl.requests]
    return {"context": _stat(contexts), "over_B": {str(b): sum(1 for c in contexts if c > b) for b in BUDGETS}}


# ---------------------------------------------------------------- the cross-check (the audit's §3.1 table)

AUDIT_ROW = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \|[^|]*\| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \| (\d+) \|$")


def audit_table(path: Path) -> dict:
    """The audit's per-day rows: {day: {requests, median, p90, max, min, compactions}} (days with numbers only)."""
    rows = {}
    for line in path.read_text().splitlines():
        m = AUDIT_ROW.match(line.strip())
        if m:
            n = [int(g.replace(",", "")) for g in m.groups()[1:]]
            rows[m.group(1)] = dict(zip(("requests", "median", "p90", "max", "min", "compactions"), n))
    return rows


def crosscheck(transcript_path: str, pin: int, audit: Path, sidechain: bool = False) -> dict:
    tl = build(transcript_path, pin, sidechain=sidechain, with_items=False)
    by_day = collections.defaultdict(list)
    for q in tl.requests:
        by_day[q.day].append(q)
    compactions = collections.Counter(day for _, day in tl.boundaries)
    expected = audit_table(audit)
    days = {}
    for day in sorted(set(by_day) | set(expected)):
        reqs = by_day.get(day, [])
        contexts = [q.context for q in reqs]
        mine = {"requests": len(reqs),
                "median": statistics.median(contexts) if contexts else None,
                "median_nearest_rank": accounting.percentile(contexts, 50),
                "p90": accounting.percentile(contexts, 90),
                "max": max(contexts) if contexts else None, "min": min(contexts) if contexts else None,
                "compactions": compactions.get(day, 0),
                "first": min(q.time for q in reqs) if reqs else None, "last": max(q.time for q in reqs) if reqs else None}
        row = {"mine": mine}
        if day in expected:
            row["audit"] = expected[day]
            row["match"] = {k: mine.get(k) == v for k, v in expected[day].items()}
            # The audit prints integers: an even count's median (the mean of the two middle values) shows truncated.
            row["median_match_after_truncation"] = mine["median"] is not None and int(mine["median"]) == expected[day]["median"]
        days[day] = row
    return {"transcript": Path(transcript_path).name, "pin": pin, "sidechain": sidechain,
            "requests": len(tl.requests), "stats": dict(sorted(tl.stats.items())), "days": days}


# ---------------------------------------------------------------- the markdown summary

def _num(value, digits=0) -> str:
    if value is None:
        return "—"
    return f"{value:,.{digits}f}"


def _pct(value) -> str:
    return "—" if value is None else f"{100 * value:.2f}%"


def _cell_rows(cells: list[dict]) -> list[str]:
    head = ("| B | L | A | rules | mode | median | p90 | max | >B | protected>B | trims | saved/trim med | "
            "req between med | net units (@0.05) | net % real | net % real (@0.1) | archived | UAA@20 | UAA@H | "
            "UAA@20 vis | UAA@H vis |")
    lines = [head, "|" + "---|" * 21]
    seen = set()
    for c in cells:
        a = c["A"]
        if c["a_invariant"]:
            key = (c["B"], c["L"], c["rules"], c["mode"], c["turn_unit"])
            if key in seen:
                continue
            seen.add(key)
            a = "any"
        u = c["use_after_archive"]
        lines.append("| " + " | ".join([
            _num(c["B"]), _num(c["L"]), str(a), c["rules"], c["mode"], _num(c["active"]["median"]),
            _num(c["active"]["p90"]), _num(c["active"]["max"]), _num(c["active"]["over_B"]),
            _pct(c["floor"]["protected_over_B_share"]), _num(c["trims"]["count"]),
            _num(c["trims"]["saved_tokens_per_trim"]["median"]), _num(c["trims"]["requests_between_trims"]["median"]),
            _num(c["cache"]["net_units"]), _pct(c["cache"]["net_share_of_real"]),
            _pct(c["cache_at_read_0_1"]["net_share_of_real"]),
            f"{u['archived_items']} ({u['scored_items']} scored)",
            str(u["at20"]["items"]), str(u["at_horizon"]["items"]),
            str(u["visible_only_at20"]["items"]), str(u["visible_only_at_horizon"]["items"])]) + " |")
    return lines


def write_summary(out: Path, stamp: str) -> Path:
    runs = sorted((json.loads(p.read_text()) for p in out.glob("run-*.json")),
                  key=lambda r: (r["label"] != "main", r["label"]))
    check = out / "crosscheck.json"
    lines = ["# T0-REPLAY results (task #346, D-105)", "",
             f"Written by `scripts/jev_trim/replay.py summary` at {stamp}. Counts, sizes, offsets and names only.",
             "Advisory: no design recommendation. The policy is D105-DESIGN-v1 §3.1; the brief is "
             "`tasks/briefs/jev-trim/T0-REPLAY-brief.md`.", "",
             "- Sizes. Exact: request contexts, cache splits, output tokens and, with thinking_size `exact` (each "
             "run's parameters say which), the thinking count of every request whose final usage record holds it, "
             "its visible blocks sized as the exact rest (output minus thinking) split by characters. Modeled: "
             "user-side content at the run's user_cpt characters per token (2.90, the brief's); a request without "
             "the count, or every request under `model` (the brief's method), sizes thinking as output minus "
             "visible characters / 3.0 and visible blocks at 3.0 characters per token.",
             "- Each segment is simulated from its real start; the active context = the exact context minus the "
             "modeled savings.",
             "- Use-after-archive (UAA) counts are a LOWER bound on need: a need that leaves no distinctive token or "
             "re-run in the record is not seen. `vis` = the visible-only variant (an archived earlier copy no longer "
             "hides a token). Thinking is never scored (its text is never read).",
             f"- Cache ratios: {CACHE_SOURCE}", ""]
    if check.exists():
        cc = json.loads(check.read_text())
        lines += [f"## Cross-check: per-day requests at pin {cc['pin']:,} ({cc['transcript']})", "",
                  "| day | requests (mine / audit) | median (mine / audit) | nearest-rank median | p90 (mine / audit) | "
                  "max (mine / audit) | min (mine / audit) | compactions (mine / audit) | fields equal | median "
                  "equal once truncated |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for day, row in cc["days"].items():
            if "audit" not in row:
                continue
            m, a = row["mine"], row["audit"]
            lines.append(f"| {day} | {m['requests']} / {a['requests']} | {_num(m['median'], 1)} / "
                         f"{_num(a['median'])} | {_num(m['median_nearest_rank'])} | {_num(m['p90'])} / "
                         f"{_num(a['p90'])} | {_num(m['max'])} / {_num(a['max'])} | {_num(m['min'])} / "
                         f"{_num(a['min'])} | {m['compactions']} / {a['compactions']} | "
                         f"{', '.join(k for k, ok in sorted(row['match'].items()) if ok)} | "
                         f"{row['median_match_after_truncation']} |")
        lines += ["", f"Days in the file with no audit row: {sum(1 for r in cc['days'].values() if 'audit' not in r)}; "
                  f"requests in the whole file at this pin: {cc['requests']:,}.", ""]
    else:  # the brief requires the cross-check: its absence is stated, never skipped in silence
        lines += ["## Cross-check: NOT RUN (no crosscheck.json in this directory)", ""]
    if not runs:
        lines += ["## Runs: NONE (no run-*.json in this directory)", ""]
    for run_ in runs:
        t = run_["timeline"]
        lines += [f"## Run `{run_['label']}`: {run_['transcript']} pinned at {run_['pin']:,} bytes "
                  f"(from offset {run_['start']:,}; thread {'sidechain' if run_['sidechain'] else 'main'})", "",
                  f"- Requests {t['requests']:,} in {t['segments']} segments; models {t['requests_by_model']}; "
                  f"context median {_num(t['context']['median'])}, p90 {_num(t['context']['p90'])}, "
                  f"max {_num(t['context']['max'])}.",
                  f"- Turns: stop-hook {t['turns']['stop']['turns']} (requests per turn median "
                  f"{_num(t['turns']['stop']['requests_per_turn']['median'], 1)}, max "
                  f"{_num(t['turns']['stop']['requests_per_turn']['max'])}); promptId {t['turns']['prompt']['turns']} "
                  f"(median {_num(t['turns']['prompt']['requests_per_turn']['median'], 1)}, max "
                  f"{_num(t['turns']['prompt']['requests_per_turn']['max'])}).",
                  f"- Calibration over {t['calibration']['pairs']:,} consecutive pairs: exact user-side residual "
                  f"{t['calibration']['exact_user_side_residual_sum']:,} vs modeled "
                  f"{_num(t['calibration']['modeled_user_side_sum'])} tokens (median residual minus modeled "
                  f"{_num(t['calibration']['residual_minus_modeled_per_request']['median'], 1)} per request); "
                  f"per-kind fit {t['calibration']['per_kind_fit']}.",
                  f"- Thinking: {t['thinking_check']}; sized {t['stats'].get('thinking_sized_exact', 0)} exactly and "
                  f"{t['stats'].get('thinking_sized_model', 0)} by the model; blocks "
                  f"{t['stats'].get('thinking_blocks', 0)}, stored text empty in "
                  f"{t['stats'].get('thinking_blocks_stored_empty', 0)}.",
                  f"- Real session (no trim): requests over B = {run_['baseline']['over_B']}; cache writes 1h "
                  f"{run_['cache_terms']['write_tokens_1h']:,}, 5m {run_['cache_terms']['write_tokens_5m']:,}; extra "
                  f"writes priced at {run_['cache_terms']['extra_write_ratio']}x.",
                  f"- Parameters: {run_['params']}", ""]
        for unit in sorted({c["turn_unit"] for c in run_["cells"]}):
            lines += [f"### Turn unit `{unit}`", ""]
            lines += _cell_rows([c for c in run_["cells"] if c["turn_unit"] == unit])
            lines.append("")
    target = out / "SUMMARY.md"
    target.write_text("\n".join(lines) + "\n")
    return target


# ---------------------------------------------------------------- the command line

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="the grid over one transcript")
    r.add_argument("--transcript", required=True)
    r.add_argument("--pin", type=int, required=True, help="byte length taken at the run's start (stat -c %%s)")
    r.add_argument("--label", required=True, help="output name: run-<label>.json")
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--start", type=int, default=0, help="byte offset of the first record to read (a compact_boundary)")
    r.add_argument("--sidechain", action="store_true", help="the thread is isSidechain true (a subagent file)")
    r.add_argument("--modes", nargs="+", choices=MODES, default=list(MODES))
    r.add_argument("--turn-units", nargs="+", choices=TURN_UNITS, default=["stop"])
    r.add_argument("--stub-tokens", type=float, default=STUB_TOKENS)
    r.add_argument("--large-input", type=float, default=LARGE_INPUT_TOKENS)
    r.add_argument("--thinking-size", choices=THINKING_SIZES, default="exact",
                   help="exact: the usage record's thinking count where present (else the model); model: the brief's "
                        "output minus visible characters / 3.0 everywhere")
    r.add_argument("--user-cpt", type=float, default=USER_CPT, help="characters per token, user-side content")
    c = sub.add_parser("crosscheck", help="per-day requests and medians with no policy, against the audit's table")
    c.add_argument("--transcript", required=True)
    c.add_argument("--pin", type=int, required=True)
    c.add_argument("--audit", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("summary", help="SUMMARY.md from the JSON files in --out")
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--stamp", default=None, help="the written-at stamp (default: now, UTC)")
    args = ap.parse_args(argv)
    if args.command == "summary":
        stamp = args.stamp or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print("wrote", write_summary(args.out, stamp))
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    if args.command == "crosscheck":
        result = crosscheck(args.transcript, args.pin, args.audit)
        (args.out / "crosscheck.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        for day, row in result["days"].items():
            if "match" not in row:
                verdict = "no audit row"
            elif all(row["match"].values()):
                verdict = "match"
            else:
                verdict = "DIFFERS in " + ", ".join(k for k, ok in sorted(row["match"].items()) if not ok)
                if not row["match"]["median"] and row["median_match_after_truncation"]:
                    verdict += " (the median is equal once truncated to the audit's integer)"
            print(day, "requests", row["mine"]["requests"], "median", row["mine"]["median"], verdict)
        return 0
    began = time.monotonic()
    tl = build(args.transcript, args.pin, start=args.start, sidechain=args.sidechain, user_cpt=args.user_cpt,
               thinking_size=args.thinking_size)
    print(f"timeline: {len(tl.requests)} requests, {len(tl.segments)} segments, "
          f"{sum(len(s.items) for s in tl.segments)} items, {time.monotonic() - began:.1f}s")
    cells = grid(tuple(args.modes), tuple(args.turn_units))
    step = max(1, len(cells) // 8)
    cell_results, cache_info = run(tl, cells, stub_tokens=args.stub_tokens, large_input_tokens=args.large_input,
                                   progress=lambda i, n: print(f"cells {i}/{n} {time.monotonic() - began:.1f}s")
                                   if i % step == 0 or i == n else None)
    result = {"schema": 1, "label": args.label, "transcript": Path(args.transcript).name, "pin": args.pin,
              "start": args.start, "sidechain": args.sidechain,
              "params": {"user_cpt": args.user_cpt, "assistant_cpt": ASSISTANT_CPT, "stub_tokens": args.stub_tokens,
                         "thinking_size": args.thinking_size,
                         "large_input_tokens": args.large_input, "K": K_TURNS, "lookahead": accounting.LOOKAHEAD,
                         "cache_read": CACHE_READ, "cache_read_alt": CACHE_READ_ALT, "cache_write_1h": CACHE_WRITE_1H,
                         "cache_write_5m": CACHE_WRITE_5M},
              "cache_source": CACHE_SOURCE, "cache_terms": cache_info, "baseline": baseline(tl),
              "timeline": timeline_summary(tl), "cells": cell_results}
    target = args.out / f"run-{args.label}.json"
    target.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(f"wrote {target} ({len(cell_results)} cells) {time.monotonic() - began:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
