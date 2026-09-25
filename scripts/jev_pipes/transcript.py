"""Stream a Claude Code session transcript into what the P1 replay needs (task #231).

Two passes over a transcript pinned at a byte length (the main session's file keeps growing while the session runs):

- `scan` (pass 1, light): the API requests (the first record of each `requestId`, with its whole-context size), the
  compaction boundaries, the tool inputs and assistant texts in order (the miss lookahead), and the candidate tool results
  with their pointers (transcript path + byte offset of the record that holds the result).
- `windows` (pass 2): rebuilds, in file order, what the plugin runtime's `$.session.messages()` returns at each wanted
  result (the jev-pruner hook reads its history there, `vendor/jev-pruner/hooks/fast-jev-output.ts:190`). The shape is the
  runtime's `SessionMessage` (`types/claude-code.d.ts` at jev-pruner 47d017c): one entry per user or assistant message,
  `text` = its text blocks joined, `toolUses` with `text`/`result`/`isError` once the transcript holds the answer,
  `toolResults` on user messages, the newest 4,096 messages, and after a compaction only the summary and what follows.

Modelling choices (stated, not measured): text blocks are joined with a newline (the pruner's own Codex reader does the
same); an assistant message is one entry per `message.id`, grown only by blocks that precede the wanted result in the file;
`isMeta` user messages are kept (they reach the model); attachment, system and bookkeeping records are not messages.
Nothing here prints or stores session text: callers hold it in memory only.
"""
from __future__ import annotations

import bisect
import collections
import json
from dataclasses import dataclass, field
from typing import Callable, Iterator

MAX_MESSAGES = 4096  # the runtime answers the newest 4,096 messages (session.messages, types/claude-code.d.ts)


@dataclass(frozen=True)
class Request:
    offset: int
    request_id: str
    context_tokens: int  # input + cache creation + cache read: the whole context the request re-sent


@dataclass(frozen=True)
class Item:
    """One unit of the miss lookahead: a tool input or an assistant text block, in file order."""

    offset: int
    kind: str  # 'tool_input' | 'assistant_text'
    tokens: frozenset
    rerun_key: tuple | None


@dataclass
class Candidate:
    path: str
    offset: int  # byte offset of the user record that holds the tool_result: the pointer
    tool_use_id: str
    tool: str
    chars: int  # characters of the result as the model read it
    is_error: bool
    persisted: bool
    rerun_key: tuple
    item_index: int = 0  # first lookahead item after the result
    tool_item_index: int = 0  # first tool call after the result (index into Index.tool_items)


@dataclass
class Index:
    path: str
    limit: int
    requests: list[Request] = field(default_factory=list)
    boundaries: list[int] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    tool_items: list[int] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    stats: collections.Counter = field(default_factory=collections.Counter)
    request_offsets: list[int] = field(default_factory=list)

    def following(self, offset: int) -> tuple[int, int | None]:
        """(requests after `offset` until the next compaction, whole-context size of the first request after `offset`).

        The second value is the miss cost's source; it is the next request even when a compaction comes first."""
        first = bisect.bisect_right(self.request_offsets, offset)
        end_boundary = bisect.bisect_right(self.boundaries, offset)
        stop = self.boundaries[end_boundary] if end_boundary < len(self.boundaries) else self.limit
        count = max(0, bisect.bisect_left(self.request_offsets, stop) - first)
        nxt = self.requests[first].context_tokens if first < len(self.requests) else None
        return count, nxt


def iter_records(path: str, limit: int, stats: collections.Counter) -> Iterator[tuple[int, dict]]:
    """Yield (byte offset, record) for every parseable line that ends before `limit`."""
    with open(path, "rb") as handle:
        offset = 0
        while offset < limit:
            raw = handle.readline()
            if not raw:
                break
            start, offset = offset, offset + len(raw)
            if offset > limit:
                stats["truncated_at_limit"] += 1
                break
            try:
                record = json.loads(raw)
            except ValueError:
                stats["unparseable_lines"] += 1
                continue
            if isinstance(record, dict):
                yield start, record


def result_text(block: dict) -> str:
    """A tool_result's content as the model read it (text blocks joined)."""
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text")
    return ""


def rerun_key(tool: str, tool_input: object) -> tuple:
    if tool == "Bash" and isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str):
        return ("Bash", " ".join(tool_input["command"].split()))
    return (tool, json.dumps(tool_input, sort_keys=True, ensure_ascii=False))


def _blocks(record: dict) -> list:
    message = record.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def scan(path: str, limit: int, tools: set[str], min_chars: int, tokenize: Callable[[str], frozenset]) -> Index:
    """Pass 1: requests, boundaries, lookahead items and the candidate results of `tools` at `min_chars` or more."""
    index = Index(path=path, limit=limit)
    calls: dict[str, tuple[str, object]] = {}
    seen_requests: set[str] = set()
    for offset, record in iter_records(path, limit, index.stats):
        kind = record.get("type")
        if kind == "system" and record.get("subtype") == "compact_boundary":
            index.boundaries.append(offset)
            continue
        if kind == "assistant":
            request_id = record.get("requestId")
            usage = (record.get("message") or {}).get("usage")
            if request_id and isinstance(usage, dict) and request_id not in seen_requests:
                seen_requests.add(request_id)
                parts = [usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")]
                if all(type(v) is int and v >= 0 for v in parts):  # declared type only; never coerce (AF-AP-72)
                    index.requests.append(Request(offset, request_id, sum(parts)))
                else:
                    index.stats["requests_with_malformed_usage"] += 1
            for block in _blocks(record):
                if block.get("type") == "text" and block.get("text"):
                    index.items.append(Item(offset, "assistant_text", tokenize(block["text"]), None))
                elif block.get("type") == "tool_use":
                    name, tool_input = block.get("name") or "?", block.get("input")
                    calls[block.get("id")] = (name, tool_input)
                    index.tool_items.append(len(index.items))
                    index.items.append(Item(offset, "tool_input", tokenize(json.dumps(tool_input, ensure_ascii=False)), rerun_key(name, tool_input)))
            continue
        if kind != "user":
            continue
        for block in _blocks(record):
            if block.get("type") != "tool_result":
                continue
            index.stats["tool_results"] += 1
            name, tool_input = calls.get(block.get("tool_use_id"), ("?", None))
            chars = len(result_text(block))
            if chars >= min_chars:
                index.stats[f"results_{min_chars}_plus"] += 1
            if name not in tools or chars < min_chars:
                continue
            tur = record.get("toolUseResult")
            persisted = isinstance(tur, dict) and isinstance(tur.get("persistedOutputPath"), str) and tur["persistedOutputPath"] != ""
            index.candidates.append(Candidate(
                path=path, offset=offset, tool_use_id=block.get("tool_use_id") or "", tool=name, chars=chars,
                is_error=block.get("is_error") is True, persisted=persisted, rerun_key=rerun_key(name, tool_input)))
    index.request_offsets = [r.offset for r in index.requests]
    item_offsets = [item.offset for item in index.items]
    tool_offsets = [index.items[i].offset for i in index.tool_items]
    for candidate in index.candidates:
        candidate.item_index = bisect.bisect_right(item_offsets, candidate.offset)
        candidate.tool_item_index = bisect.bisect_right(tool_offsets, candidate.offset)
    index.stats["requests"] = len(index.requests)
    index.stats["compactions"] = len(index.boundaries)
    return index


@dataclass
class Snapshot:
    """What the runtime would hand the hook at one result; valid only until the generator advances."""

    offset: int
    record: dict  # the user record holding the result (its toolUseResult is the tool's record)
    block: dict  # the tool_result block
    call_input: object  # the tool_use input of the call this result answers
    messages: list  # the SessionMessage window, newest MAX_MESSAGES
    history_tokens: set  # distinctive tokens of every message in the window


def windows(path: str, limit: int, wanted: set[int], tokenize: Callable[[str], frozenset]) -> Iterator[Snapshot]:
    """Pass 2: yield a Snapshot at each wanted offset, before that result joins the window."""
    stats: collections.Counter = collections.Counter()
    window: list[dict] = []
    by_message_id: dict[str, dict] = {}
    uses: dict[str, dict] = {}
    inputs: dict[str, object] = {}
    history_tokens: set = set()

    def add_tokens(text: str) -> None:
        if text:
            history_tokens.update(tokenize(text))

    for offset, record in iter_records(path, limit, stats):
        kind = record.get("type")
        if kind == "system" and record.get("subtype") == "compact_boundary":
            window, by_message_id, uses = [], {}, {}
            history_tokens = set()
            continue
        if kind == "assistant":
            message_id = (record.get("message") or {}).get("id") or f"record@{offset}"
            entry = by_message_id.get(message_id)
            if entry is None:
                entry = {"role": "assistant", "text": "", "toolUses": []}
                by_message_id[message_id] = entry
                window.append(entry)
            for block in _blocks(record):
                if block.get("type") == "text" and block.get("text"):
                    entry["text"] = block["text"] if not entry["text"] else entry["text"] + "\n" + block["text"]
                    add_tokens(block["text"])
                elif block.get("type") == "tool_use":
                    use = {"tool_use_id": block.get("id") or "", "tool": block.get("name") or "?", "input": block.get("input") or {}}
                    uses[use["tool_use_id"]] = use
                    inputs[use["tool_use_id"]] = block.get("input")
                    entry["toolUses"].append(use)
                    add_tokens(json.dumps(use["input"], ensure_ascii=False))
            continue
        if kind != "user":
            continue
        blocks = _blocks(record)
        results = [b for b in blocks if b.get("type") == "tool_result"]
        for block in results:
            if offset in wanted:
                yield Snapshot(offset, record, block, inputs.get(block.get("tool_use_id")), window[-MAX_MESSAGES:], history_tokens)
        texts = [b.get("text", "") for b in blocks if b.get("type") == "text" and b.get("text")]
        message = {"role": "user", "text": "\n".join(texts), "toolUses": []}
        if results:
            message["toolResults"] = []
            tur = record.get("toolUseResult")
            for block in results:
                text = result_text(block)
                item = {"tool_use_id": block.get("tool_use_id") or "", "text": text, "isError": block.get("is_error") is True}
                if tur is not None:
                    item["result"] = tur
                message["toolResults"].append(item)
                use = uses.get(item["tool_use_id"])
                if use is not None:
                    use["text"] = text
                    if tur is not None:
                        use["result"] = tur
                    if item["isError"]:
                        use["isError"] = True
                add_tokens(text)
        for text in texts:
            add_tokens(text)
        if message["text"] or results:
            window.append(message)
