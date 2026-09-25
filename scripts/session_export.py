#!/usr/bin/env python3
"""Every session transcript as an ordered, scrubbed stream of calls and results, for the RWKV student and the Jev pipelines
(task #252; D-084, D-086, D-087; brief tasks/briefs/jev-laya/SESSION-EXPORT-brief.md with AMENDMENTS 1 and 2).

Sources: every *.jsonl under every project folder of /root/.claude/projects/ (the harness files a session under the slug of
its launch directory, and one session id can hold a transcript in two folders). `src` is the path under that root.

One JSON object per event, one per line, in source order: seq (from 0 in one transcript), src, line (its 1-based JSONL
line), ts, role, kind, tool, call_id, text, truncated, outcome, model, stop_reason (the brief's D-1 and G2).

Roles. A user text or a queued command names its speaker in the harness's own field `origin.kind`: `human` is the owner,
`coordinator` the coordinator (its messages to a subagent), `peer` an agent (a subagent's message to the coordinator); any
other kind (`task-notification`) is a system notification. With no `origin`: a meta record or a harness prefix (a task
notification, a system reminder, local command output, an interrupt marker) is the system's, other text is the owner's in
a session transcript (one that sits directly in its project folder) and the coordinator's in a subagent or workflow agent
(its prompt and follow-ups). `Stop hook feedback:` text, hook attachments and stop-hook summaries are the hook's; a
compaction summary (`isCompactSummary`) is a `summary`; assistant blocks are the coordinator's in a session transcript and
the agent's elsewhere; a tool result, a Bash file change and a pruner archive are the tool's; system records, the other
attachments and a workflow journal's records are the system's.

Kinds: text; thinking (a block whose `thinking` holds plain text; a signature-only block is counted, not exported);
tool_call (text = the input as canonical JSON); tool_result; hook; notification; summary; harness_notice (the harness's
`edited_text_file` attachment: a file changed outside the model, G1); api_error (an assistant record with
`isApiErrorMessage`, a system record with subtype `api_error`, G2); file_change (one per file in the result record's
`toolUseResult.bashEditDiff`, right after the result, G5); pruner_archive (the jev-pruner's
`<cwd>/.claude/fast-jev-output/bash-<tool_use_id>.txt`, the full output of a result it trimmed, right after that result,
AMENDMENT 2). Harness configuration and meters (SKIP_ATTACHMENTS) and bookkeeping record types are counted per type, not
exported. A task notification is kept once per identity (its `<task-id>`, `<tool-use-id>`, `<status>` and `<event>`; one
with no task id is never merged, G4).

Outcome, on a tool_result: only fields the harness wrote -- `is_error` (the block's field), `exit_code` (the leading
`Exit code N` line of an error result), `timed_out_after_ms` (`toolUseResult.timedOutAfterMs`), `denial_kind` (the
record's `toolDenialKind`); on a stop-hook summary: `hook_errors` (`hookErrors`, scrubbed). Null on every other event.
`model` and `stop_reason` are the assistant record's `message.model` and `message.stop_reason`; null for any other record.

Scrubbing (D-2, G6). Every text passes transcript_export.scrub_payload, run to a fixed point: named rules first, then the
coarse opaque-run rule, whose match becomes `[opaque:<first 12 hex of HMAC-SHA256(key, value)>]` -- a stable, keyed
pseudonym, so a commit id still joins a push to its CI run. The key is 32 random bytes in KEY_PATH (made once by `init-key`,
mode 0600, never exported or printed); with no key, a short key or a key others can read, the export refuses. A Read,
Write or Edit (and MultiEdit, NotebookEdit) whose path names a secret file (SECRET_PATH) keeps its event, but its input and
its result become DROPPED; so do an attachment and a file change whose file path names one. Any other call whose input
names one keeps its scrubbed input, and its result (and its file changes and archive) pass transcript_export.scrub_strict;
so does a result whose call is not in the transcript. Cap (D-3, G3): a Read result, a Write input, a file change and a
pruner archive keep their first 98,304 and last 32,768 characters of a text over 131,072; every other event its first
24,576 and last 8,192 of a text over 32,768; scrubbed first; if the seam forms a secret shape, the cut moves inward and
`truncated` records what was kept.

convert() turns one transcript from a start byte into events and returns the offset after its last complete line and a
state to pass back, so a file converted in parts gives the same events as one pass (AMENDMENT 2); the batch export calls it
from 0. Files (D-4, D-5): each source is read to a byte offset fixed before any work (the end of its last complete line),
or taken from --offsets <manifest> and checked against that manifest's input sha256 (the pruner archives likewise); one
<src>.xz (lzma, preset 6) per source; manifest.json last. The leak gate (D-6) decompresses every output as a stream and
counts, per pattern, each match of the extended scrubber's shapes that the scrubber would still change, each test canary
and the key's printed forms; it prints counts only.

usage: session_export.py init-key [--key PATH]
       session_export.py export --out DIR [--root DIR] [--offsets MANIFEST] [--jobs N] [--key PATH] [--archive-dir DIR]
       session_export.py gate DIR [--jobs N] [--key PATH]
exit:  0 done and the gate found nothing; 2 bad input (usage, no sources, a used out dir, a missing or loose key, an input or
       archive changed under its offset); 3 the gate found a secret shape or a canary (the manifest records it;
       ship_to_pc.py refuses it). Standard library only. It never prints transcript text.
"""
import argparse
import base64
import concurrent.futures
import datetime
import glob
import hashlib
import hmac
import json
import lzma
import os
import re
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from transcript_export import PAYLOAD_PATTERNS, SECRET_PATTERNS, scrub_payload, scrub_strict  # noqa: E402

PROJECTS = "/root/.claude/projects"
KEY_PATH = "/root/.config/session-export/pseudonym.key"
KEY_BYTES = 32
KEY_ID_MSG = b"session-export key id"
CAP, HEAD, TAIL = 32768, 24576, 8192
BIG_CAP, BIG_HEAD, BIG_TAIL = 131072, 98304, 32768         # G3: Read results, Write inputs, file changes, pruner archives
XZ_PRESET = 6
DROPPED = "[payload dropped: secret path]"
UNSETTLED = "[payload dropped: scrub did not settle]"
SEAMLESS = "[payload dropped: no clean cut]"
SECRET_PATH = re.compile(r"\.env(?![A-Za-z0-9_])|qwen-builder/api-key|qwen-jev/omniroute\.key|\.hermes/profiles/"
                         r"|session-export/pseudonym\.key")
FILE_TOOLS = {"Read": "file_path", "Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path",
              "NotebookEdit": "notebook_path"}
PATH_KEYS = frozenset(("filename", "displayPath", "path", "filePath", "file_path"))
SKIP_ATTACHMENTS = frozenset((
    "total_tokens_reminder", "batching_reminder_sent",                      # meters
    "prompt_snapshot", "skill_listing", "deferred_tools_delta", "deferred_tools_record", "mcp_instructions_delta",
    "agent_listing_delta", "dynamic_skill", "command_permissions", "instructions", "nested_memory", "invoked_skills",
    "environment", "auto_mode", "auto_mode_exit", "model", "date", "session_context", "remote_session_change",
    "output_style", "output_style_instructions", "ultra_effort_enter", "ultra_effort_exit", "thinking_drop"))
ENVELOPE = frozenset(("uuid", "parentUuid", "logicalParentUuid", "sessionId", "timestamp", "cwd", "gitBranch", "version",
                      "userType", "entrypoint", "isSidechain", "slug", "agentId", "requestId", "promptId"))
HARNESS_PREFIXES = ("<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION", "<local-command-",
                    "[Request interrupted")
ORIGIN_ROLE = {"human": "owner", "coordinator": "coordinator", "peer": "agent"}
EXIT_LINE = re.compile(r"Exit code (\d+)\Z")
NOTE_TAGS = tuple(re.compile(r"<%s>(.*?)</%s>" % (t, t), re.S) for t in ("task-id", "tool-use-id", "status", "event"))
ARCHIVE_DIR = os.path.join(".claude", "fast-jev-output")
ARCHIVE_NAME = re.compile(r"bash-([A-Za-z][A-Za-z0-9_\-]*)\.txt\Z")   # the pruner's fallback name is a clock: no call id
CWD = re.compile(rb'"cwd":"((?:[^"\\]|\\.)*)"')
PSEUDO = re.compile(r"\[opaque:[0-9a-f]{12}\]")
PATTERN_NAMES = ("private-key", "credential", "bearer", "sk-key", "github-token", "google-key", "slack-token",
                 "bridge-link", "opaque-run", "bridge-host", "bearer-tail", "basic-auth", "url-password")


def _z(tag):
    """A fake secret body: 18 letters drawn from a hash of the tag, then `7w`. No two canaries share an 8-character
    window, and none meets a hex digest. Assembled at import, so no source line (and no transcript that records this
    file) holds a whole canary. Never print one."""
    h = hashlib.sha256(("session-export canary " + tag).encode()).hexdigest()
    return "".join("GHJKLMNPQRSTVWXY"[int(c, 16)] for c in h[:18]) + "7w"


def _host(tag):
    return "zq-" + _z(tag).lower()


# The test canaries: tests/test_session_export.py plants each in its payload shape, and the gate counts them in every
# export.
CANARIES = {
    "bridge-host": _host("bh1"), "bridge-token": _z("bt1"), "gh-thinking": "ghp_" + _z("gt1"),
    "signature": "Eq" + _z("sg1"), "env-write": _z("ew1"), "env-write-2": _z("ew2"), "bridge-host-2": _host("bh2"),
    "bridge-token-2": _z("bt2"), "env-line": _z("el1"), "env-grep": _z("eg1"), "keyfile-bash": _z("kb1") + "x9y8",
    "bridge-host-3": _host("bh3"), "curl-token": _z("ct1"), "bearer": _z("br1") + "+" + _z("br2") + "==",
    "bridge-host-4": _host("bh4"), "url-password": _z("up1"), "basic-auth": _z("ba1") + "Zm9vYmFy",
    "pem": _z("pm1") + "AAKCAQx7Qe", "keyfile": _z("kf1"), "hermes-old": _z("ho1"), "hermes-new": _z("hn1"),
    "grep-tool": _z("gr1"), "gh-result": "ghp_" + _z("gr2"), "cap-straddle": _z("cs1") + _z("cs2"),
    "bridge-host-5": _host("bh5"), "queued-token": _z("qt1"), "hook-bearer": _z("hb1"), "att-file": _z("af1"),
    "att-edited": _z("ae1"), "stop-hook-host": _host("sh1"), "compact-token": _z("cp1"), "last-prompt": _z("lp1"),
    "queue-op": _z("qo1"), "orphan": _z("or1"), "sub-prompt": _z("sp1"), "sk-key": _z("sk1") + "abcdef",
    "sub-followup": _z("sf1"), "journal-gh": "ghp_" + _z("jg1"),
    "api-error-bearer": _z("ab1"), "notice-token": _z("nt1"), "bash-diff-key": _z("dk1"), "bash-diff-env": _z("de1"),
    "long-token": _z("lt1") + _z("lt2"), "archive-token": _z("at1"), "archive-env": _z("ae2"), "pkey-read": _z("pk1"),
}


class KeyRefused(Exception):
    """The pseudonym key is missing, short or readable by others: the export refuses (G6)."""


class ArchiveChanged(Exception):
    """A pruner archive no longer holds the bytes its manifest entry names."""


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _fix(s):
    """A lone surrogate (from a JSON escape) cannot be written as UTF-8; it becomes `?`."""
    return s.encode("utf-8", "replace").decode("utf-8")


def _inc(counter, key, n=1):
    counter[key] = counter.get(key, 0) + n


def _paths(obj):
    """Every string under a file-path key, at any depth of an attachment."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in PATH_KEYS and isinstance(v, str):
                yield v
            else:
                yield from _paths(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _paths(v)


def _image(part):
    src = part.get("source") if isinstance(part.get("source"), dict) else {}
    return "[image: %s]" % (src.get("media_type") if isinstance(src.get("media_type"), str) else "?")


def _text_of(content):
    """A message content or a tool result's content as one text: text parts joined, an image as a note (its data never)."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return canon(content)
    parts = []
    for p in content:
        t = p.get("type") if isinstance(p, dict) else None
        if t == "text":
            parts.append(p.get("text") if isinstance(p.get("text"), str) else "")
        elif t == "image":
            parts.append(_image(p))
        elif t == "tool_reference":
            parts.append("[tool_reference: %s]" % p.get("tool_name"))
        else:
            parts.append(canon(p))
    return "\n".join(parts)


def note_identity(text):
    """G4: a task notification's identity from its own fields; None for other text and for one with no task id."""
    s = text.lstrip()
    if not s.startswith("<task-notification>"):
        return None
    vals = [(m.group(1).strip() if m else "") for m in (rx.search(s) for rx in NOTE_TAGS)]
    return "\x1f".join(vals) if vals[0] else None


def diff_text(path, entry):
    """G5: one file of a bashEditDiff as text: its path, then each hunk's header and lines."""
    head = path + (" (new file)" if entry.get("created") is True else " (deleted)" if entry.get("deleted") is True else "")
    out = [head]
    for h in entry.get("hunks") or []:
        if isinstance(h, dict):
            out.append("@@ -%s,%s +%s,%s @@" % (h.get("oldStart"), h.get("oldLines"), h.get("newStart"), h.get("newLines")))
            out.extend(x for x in h.get("lines") or [] if isinstance(x, str))
    return "\n".join(out)


def _read_regular(path):
    """One open of a regular file, never through a link and never blocking on a FIFO (AF-AP-70); its bytes and stat."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise OSError("not a regular file: %s" % path)
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return b"".join(chunks), st
            chunks.append(chunk)
    finally:
        os.close(fd)


def load_key(path):
    """G6: the pseudonym key -- exactly KEY_BYTES bytes, readable by its owner only. KeyRefused otherwise; no fallback."""
    try:
        key, st = _read_regular(path)
    except OSError:
        raise KeyRefused("no pseudonym key at %s (make it once: session_export.py init-key)" % path)
    if len(key) != KEY_BYTES or st.st_mode & 0o077:
        raise KeyRefused("the pseudonym key at %s must be %d bytes with mode 0600" % (path, KEY_BYTES))
    return key


def key_id(key):
    return hmac.new(key, KEY_ID_MSG, hashlib.sha256).hexdigest()[:12]


def key_forms(key):
    """The printed forms of the key the gate must never find in an export."""
    return {"pseudonym-key-hex": key.hex(), "pseudonym-key-HEX": key.hex().upper(),
            "pseudonym-key-b64": base64.b64encode(key).decode(), "pseudonym-key-b64url": base64.urlsafe_b64encode(key).decode()}


def pseudonymizer(key):
    """G6: the opaque-run rule's replacement in this export: a stable pseudonym keyed by HMAC-SHA256."""
    return lambda m: "[opaque:%s]" % hmac.new(key, m.group(0).encode("utf-8"), hashlib.sha256).hexdigest()[:12]


def settle(text, strict, opaque):
    """The scrubber run to a fixed point (at most 4 passes), so the gate's check holds by construction; None if not."""
    f = scrub_strict if strict else scrub_payload
    for _ in range(4):
        out = f(text, opaque)
        if out == text:
            return out if not strict or scrub_payload(out, opaque) == out else None
        text = out
    return None


def cap(text, strict, opaque, head, tail):
    """D-3: the head and tail of an over-long text; the cut moves inward until the seam forms no secret shape."""
    for k in (0, 64, 256, 1024, 4096, tail):
        h, t = head - k, tail - k
        out = text[:h] + (text[len(text) - t:] if t else "")
        if scrub_payload(out, opaque) == out and (not strict or scrub_strict(out, opaque) == out):
            return out, {"kept_head": h, "kept_tail": t, "dropped": len(text) - h - t}
    return None, None


def call_mode(name, inp, text):
    """"drop" for a file tool on a secret path, "strict" for any other call whose input names one, else None."""
    key = FILE_TOOLS.get(name)
    if key and isinstance(inp, dict) and isinstance(inp.get(key), str) and SECRET_PATH.search(inp[key]):
        return "drop"
    return "strict" if SECRET_PATH.search(text) else None


def read_archive(entry):
    try:
        data, _ = _read_regular(entry["path"])
    except OSError:
        data = b""
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ArchiveChanged("a pruner archive changed after its offsets were fixed: %s" % os.path.basename(entry["path"]))
    return data.decode("utf-8", "replace")


class Source:
    """One transcript's events, counts and state (AMENDMENT 2: the state a part hands to the next)."""

    def __init__(self, src, key, archives, sink, state=None):
        self.src, self.sink, self.archives = src, sink, archives
        self.main = src.count("/") == 1              # a session transcript sits directly in its project folder
        self.opaque = pseudonymizer(key)
        state = json.loads(json.dumps(state)) if state else {}
        self.offset, self.line, self.seq = state.get("offset", 0), state.get("line", 0), state.get("seq", 0)
        self.calls = {k: tuple(v) for k, v in state.get("calls", {}).items()}    # tool_use id -> (tool name, mode)
        self.notes = set(state.get("notes", []))
        self.archived = state.get("archived", [])
        self.st = state.get("st") or {
            "bad_lines": 0, "events": {}, "capped": {}, "seam_adjusted": 0, "dropped_secret_path": 0, "strict_results": 0,
            "unsettled": 0, "thinking_signature_only": 0, "duplicate_notifications": 0, "file_changes_unrecorded": 0,
            "pruner_archives": 0, "pseudonyms": 0, "skipped_records": {}, "skipped_attachments": {}}

    def state(self):
        return {"src": self.src, "offset": self.offset, "line": self.line, "seq": self.seq,
                "calls": {k: list(v) for k, v in self.calls.items()}, "notes": sorted(self.notes),
                "archived": list(self.archived), "st": self.st}

    def emit(self, line, ts, role, kind, text, tool=None, call_id=None, outcome=None, mode=None, model=None,
             stop_reason=None):
        """mode None: scrub_payload; "strict": scrub_strict; "drop": the text becomes DROPPED."""
        st, truncated = self.st, None
        big = kind in ("file_change", "pruner_archive") or (kind, tool) in (("tool_result", "Read"), ("tool_call", "Write"))
        limit, head, tail = (BIG_CAP, BIG_HEAD, BIG_TAIL) if big else (CAP, HEAD, TAIL)
        if mode == "drop":
            text = DROPPED
            st["dropped_secret_path"] += 1
        else:
            st["strict_results"] += mode == "strict"
            text = settle(_fix(text), mode == "strict", self.opaque)
            if text is None:
                text = UNSETTLED
                st["unsettled"] += 1
            elif len(text) > limit:
                text, truncated = cap(text, mode == "strict", self.opaque, head, tail)
                if text is None:
                    text = SEAMLESS
                    st["unsettled"] += 1
                else:
                    _inc(st["capped"], kind)
                    st["seam_adjusted"] += truncated["kept_head"] != head
            st["pseudonyms"] += len(PSEUDO.findall(text))
        ev = {"seq": self.seq, "src": self.src, "line": line, "ts": ts, "role": role, "kind": kind,
              "tool": _fix(tool) if isinstance(tool, str) else None,
              "call_id": _fix(call_id) if isinstance(call_id, str) else None,
              "text": text, "truncated": truncated, "outcome": outcome,
              "model": _fix(model) if isinstance(model, str) else None,
              "stop_reason": _fix(stop_reason) if isinstance(stop_reason, str) else None}
        self.seq += 1
        _inc(st["events"], kind)
        self.sink(ev)

    def speaker(self, holder, text):
        """(role, kind) of a user text or a queued command (see the module docstring)."""
        s = text.lstrip()
        if holder.get("isCompactSummary"):
            return "system", "summary"
        if s.startswith("Stop hook feedback:"):
            return "hook", "hook"
        origin = holder.get("origin")
        kind = origin.get("kind") if isinstance(origin, dict) else None
        if isinstance(kind, str):
            return (ORIGIN_ROLE[kind], "text") if kind in ORIGIN_ROLE else ("system", "notification")
        if holder.get("isMeta") or s.startswith(HARNESS_PREFIXES):
            return "system", "notification"
        return ("owner" if self.main else "coordinator"), "text"

    def repeated(self, text):
        """G4: True for the second record of one notification identity (it is counted, not exported)."""
        ident = note_identity(text)
        if ident is None:
            return False
        if ident in self.notes:
            self.st["duplicate_notifications"] += 1
            return True
        self.notes.add(ident)
        return False

    def record(self, n, r):
        t = r.get("type")
        ts = _fix(r["timestamp"]) if isinstance(r.get("timestamp"), str) else None
        if t == "assistant":
            self.assistant(n, ts, r)
        elif t == "user":
            self.user(n, ts, r)
        elif t == "attachment":
            self.attachment(n, ts, r)
        elif t == "system":
            self.system(n, ts, r)
        elif t in ("started", "result"):             # a workflow journal
            self.emit(n, ts, "system", "notification", canon(r))
        else:
            _inc(self.st["skipped_records"], str(t))

    def assistant(self, n, ts, r):
        msg = r.get("message") if isinstance(r.get("message"), dict) else {}
        content, model, stop = msg.get("content"), msg.get("model"), msg.get("stop_reason")
        if r.get("isApiErrorMessage") is True:        # G2: the harness's own error text in an assistant record
            self.emit(n, ts, "system", "api_error", _text_of(content), model=model, stop_reason=stop)
            return
        role = "coordinator" if self.main else "agent"
        if isinstance(content, str):
            self.emit(n, ts, role, "text", content, model=model, stop_reason=stop)
            return
        for b in content if isinstance(content, list) else []:
            bt = b.get("type") if isinstance(b, dict) else None
            if bt == "text":
                self.emit(n, ts, role, "text", b.get("text") if isinstance(b.get("text"), str) else "", model=model,
                          stop_reason=stop)
            elif bt in ("thinking", "redacted_thinking"):
                if bt == "thinking" and isinstance(b.get("thinking"), str) and b["thinking"]:
                    self.emit(n, ts, role, "thinking", b["thinking"], model=model, stop_reason=stop)
                else:
                    self.st["thinking_signature_only"] += 1
            elif bt == "tool_use":
                name, cid, inp = b.get("name"), b.get("id"), b.get("input")
                text = canon(inp)
                mode = call_mode(name, inp, text)
                if isinstance(cid, str):
                    self.calls[cid] = (name, mode)
                self.emit(n, ts, role, "tool_call", text, tool=name, call_id=cid, mode="drop" if mode == "drop" else None,
                          model=model, stop_reason=stop)
            else:
                self.emit(n, ts, role, "text", canon(b), model=model, stop_reason=stop)

    def user(self, n, ts, r):
        msg = r.get("message") if isinstance(r.get("message"), dict) else {}
        content = msg.get("content")
        if not isinstance(content, list):
            text = _text_of(content)
            if not self.repeated(text):
                role, kind = self.speaker(r, text)
                self.emit(n, ts, role, kind, text)
            return
        blocks = [b for b in content if isinstance(b, dict)]
        text = "\n".join(b["text"] for b in blocks if b.get("type") == "text" and isinstance(b.get("text"), str))
        if not any(b.get("type") == "tool_result" for b in blocks) and self.repeated(text):
            return
        role, kind = self.speaker(r, text)
        for b in blocks:
            if b.get("type") == "tool_result":
                self.tool_result(n, ts, r, b)
            else:
                self.emit(n, ts, role, kind, _text_of([b]))

    def tool_result(self, n, ts, r, b):
        cid = b.get("tool_use_id") if isinstance(b.get("tool_use_id"), str) else None
        name, mode = self.calls.get(cid, (None, "strict"))          # a result with no call here: strict
        text = _text_of(b.get("content"))
        outcome = {}
        if isinstance(b.get("is_error"), bool):
            outcome["is_error"] = b["is_error"]
        if b.get("is_error") is True:
            m = EXIT_LINE.match(text.split("\n", 1)[0])
            if m:
                outcome["exit_code"] = int(m.group(1))
        tur = r.get("toolUseResult") if isinstance(r.get("toolUseResult"), dict) else {}
        if type(tur.get("timedOutAfterMs")) is int:
            outcome["timed_out_after_ms"] = tur["timedOutAfterMs"]
        if isinstance(r.get("toolDenialKind"), str):
            outcome["denial_kind"] = r["toolDenialKind"]
        self.emit(n, ts, "tool", "tool_result", text, tool=name, call_id=cid, outcome=outcome, mode=mode)
        entry = self.archives.get(cid) if cid else None
        if entry is not None:                         # AMENDMENT 2: what the pruner kept from the model, in full
            self.emit(n, ts, "tool", "pruner_archive", read_archive(entry), tool=name, call_id=cid, mode=mode)
            self.st["pruner_archives"] += 1
            self.archived.append(cid)
        diff = tur.get("bashEditDiff")
        if isinstance(diff, dict):                    # G5: the files the call changed, in the harness's order
            files = {f["filePath"]: f for f in diff.get("files") or [] if isinstance(f, dict) and isinstance(f.get("filePath"), str)}
            changed = [p for p in diff.get("changedFiles") or [] if isinstance(p, str)]
            changed += [p for p in files if p not in changed]
            for p in changed:
                body = diff_text(p, files[p]) if p in files else p + "\n[diff not recorded]"
                self.emit(n, ts, "tool", "file_change", body, tool=name, call_id=cid,
                          mode="drop" if SECRET_PATH.search(p) else mode)
            if type(diff.get("moreFiles")) is int and diff["moreFiles"] > 0:
                self.st["file_changes_unrecorded"] += diff["moreFiles"]

    def attachment(self, n, ts, r):
        a = r.get("attachment") if isinstance(r.get("attachment"), dict) else {}
        at = a.get("type") if isinstance(a.get("type"), str) else "?"
        if at in SKIP_ATTACHMENTS:
            _inc(self.st["skipped_attachments"], at)
            return
        mode = "drop" if any(SECRET_PATH.search(p) for p in _paths(a)) else None
        if at == "queued_command":
            text = _text_of(a.get("prompt"))
            if not self.repeated(text):
                role, kind = self.speaker(a, text)
                self.emit(n, ts, role, kind, text, mode=mode)
        elif at.startswith("hook_"):
            self.emit(n, ts, "hook", "hook", canon(a), mode=mode)
        elif at == "edited_text_file":                # G1: a file changed outside the model
            self.emit(n, ts, "system", "harness_notice", canon(a), mode=mode)
        else:
            self.emit(n, ts, "system", "notification", canon(a), mode=mode)

    def system(self, n, ts, r):
        body = canon({k: v for k, v in r.items() if k not in ENVELOPE})
        sub = r.get("subtype")
        if sub == "api_error":                        # G2
            self.emit(n, ts, "system", "api_error", body)
        elif sub == "stop_hook_summary":
            errs = r.get("hookErrors")
            outcome = {}
            if isinstance(errs, list):
                outcome["hook_errors"] = [self.settled(e) for e in errs if isinstance(e, str)]
            self.emit(n, ts, "hook", "hook", body, outcome=outcome)
        else:
            self.emit(n, ts, "system", "notification", body)

    def settled(self, text):
        out = settle(_fix(text), False, self.opaque)
        if out is None:
            self.st["unsettled"] += 1
            return UNSETTLED
        return out


def convert(path, src=None, start=0, state=None, end=None, key=None, archives=None, sink=None, hasher=None):
    """AMENDMENT 2: convert one transcript from byte `start` -- 0, or the offset a previous call returned, with the state
    it returned -- through its last complete line (or through `end`, a line boundary). Returns (events, offset, state):
    the events in source order (an empty list when `sink` took each one), the offset after the last complete line read,
    and the state to pass with that offset next time. Converting a file in parts gives the same events as one pass.
    `key` is the pseudonym key (required; no fallback); `archives` maps a call id to its pruner archive entry; `hasher`,
    when given, is updated with every byte read."""
    if not isinstance(key, bytes) or len(key) != KEY_BYTES:
        raise KeyRefused("convert() needs the %d-byte pseudonym key" % KEY_BYTES)
    if state is not None and state.get("offset") != start:
        raise ValueError("start %d is not the offset its state was returned with" % start)
    events = []
    s = Source(src if src is not None else os.path.relpath(path, PROJECTS), key, archives or {},
               sink if sink is not None else events.append, state)
    with open(path, "rb") as fh:
        if start:
            fh.seek(start - 1)
            if fh.read(1) != b"\n":
                raise ValueError("start %d is not at a line boundary" % start)
        pos = start
        while end is None or pos < end:
            raw = fh.readline() if end is None else fh.readline(end - pos)
            if not raw.endswith(b"\n"):               # the end of the file, or a line the writer has not finished
                break
            pos, s.line = pos + len(raw), s.line + 1
            if hasher is not None:
                hasher.update(raw)
            try:
                r = json.loads(raw)
            except (ValueError, RecursionError):
                r = None
            if isinstance(r, dict):
                s.record(s.line, r)
            else:
                s.st["bad_lines"] += 1
    s.offset = pos
    return events, pos, s.state()


def fixed_offset(path):
    """D-4: the end of the file's last complete line now (a live transcript keeps growing; a cut line would not parse)."""
    pos = os.path.getsize(path)
    with open(path, "rb") as fh:
        while pos > 0:
            step = min(1 << 20, pos)
            fh.seek(pos - step)
            i = fh.read(step).rfind(b"\n")
            if i >= 0:
                return pos - step + i + 1
            pos -= step
    return 0


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def archive_dirs(root, sources, extra):
    """AMENDMENT 2: the pruner writes under the session's working directory, so every `cwd` a record names (read up to the
    fixed offsets) is a place to look, with the directories given by hand; only those that exist are kept."""
    cwds = set()
    for src, offset in sources:
        done = 0
        with open(os.path.join(root, src), "rb") as fh:
            for raw in fh:
                if done >= offset:
                    break
                done += len(raw)
                m = CWD.search(raw)
                if m:
                    try:
                        cwds.add(json.loads(b'"' + m.group(1) + b'"'))
                    except ValueError:
                        pass
    dirs = {os.path.join(c, ARCHIVE_DIR) for c in cwds if os.path.isabs(c)} | {os.path.abspath(d) for d in extra}
    return sorted(d for d in dirs if os.path.isdir(d))


def find_archives(dirs):
    """Every pruner archive now: its path, the call id its name carries (None for the pruner's clock-named fallback), its
    size and sha256. An entry that is not a regular file is listed with `skipped`, never read through."""
    out = []
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "bash-*.txt"))):
            m = ARCHIVE_NAME.match(os.path.basename(p))
            try:
                data, _ = _read_regular(p)
            except OSError:
                out.append({"path": p, "call_id": None, "bytes": 0, "sha256": None, "skipped": "not a regular file"})
                continue
            out.append({"path": p, "call_id": m.group(1) if m else None, "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})
    return out


def archive_unchanged(entry):
    """An --offsets rerun reads the archives its manifest names, each with the same bytes; archives written since are not
    in that list, as lines past an offset are not."""
    if entry.get("sha256") is None:
        return True
    try:
        data, _ = _read_regular(entry["path"])
    except OSError:
        return False
    return hashlib.sha256(data).hexdigest() == entry["sha256"]


def export_source(root, src, offset, out_dir, expect_sha, key, archives):
    """One source to <out_dir>/<src>.xz through convert() from 0, read only up to its offset; its manifest entry."""
    dest = os.path.join(out_dir, src + ".xz")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    h = hashlib.sha256()
    try:
        with lzma.open(dest + ".part", "wb", preset=XZ_PRESET) as out:
            def write(ev):
                out.write((json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
            _, pos, state = convert(os.path.join(root, src), src, 0, None, offset, key, archives, write, h)
    except ArchiveChanged as e:
        os.remove(dest + ".part")
        return {"src": src, "error": str(e)}
    sha = h.hexdigest()
    if pos != offset or (expect_sha is not None and sha != expect_sha):
        os.remove(dest + ".part")
        return {"src": src, "error": "input changed under its offset" if pos == offset else "input shorter than its offset"}
    os.replace(dest + ".part", dest)
    st = state["st"]
    for k in ("events", "capped", "skipped_records", "skipped_attachments"):
        st[k] = dict(sorted(st[k].items()))
    return {"src": src, "offset": offset, "input_sha256": sha, "output": src + ".xz", "output_sha256": sha256_file(dest),
            "output_bytes": os.path.getsize(dest), "lines": state["line"], **st, "archived": sorted(state["archived"])}


def gate_patterns():
    pats = list(SECRET_PATTERNS) + list(PAYLOAD_PATTERNS)
    names = PATTERN_NAMES if len(PATTERN_NAMES) == len(pats) else tuple("pattern-%d" % i for i in range(len(pats)))
    return list(zip(names, pats))


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_\-]*")
IDENT_FIELDS = ("tool", "call_id")


def gate_file(path, extra=None):
    """D-6 over one output, decompressed as a stream: per pattern, the matches its rule would still change, in every
    string of every event; per canary (and per printed form of the key, `extra`), its occurrences. Counts only. One
    exemption: the coarse opaque-run rule (40+ identifier characters) skips a `tool` or `call_id` that is one identifier,
    because the harness names its tools (`mcp__Claude_Code_Remote__register_repo_root` is 43 characters) and its call
    ids; every other rule and every canary still reads them."""
    pats = gate_patterns()
    needles = dict(CANARIES, **(extra or {}))
    res = {"events": 0, "bad_lines": 0, "patterns": {name: 0 for name, _ in pats}, "canaries": {c: 0 for c in needles}}
    with lzma.open(path, "rb") as fh:
        for raw in fh:
            try:
                ev = json.loads(raw)
            except ValueError:
                res["bad_lines"] += 1
                continue
            res["events"] += 1
            for field, value in (ev.items() if isinstance(ev, dict) else [(None, ev)]):
                ident = field in IDENT_FIELDS and isinstance(value, str) and IDENT.fullmatch(value)
                for s in _strings(value):
                    for name, (pat, rep) in pats:
                        if ident and name == "opaque-run":
                            continue
                        for m in pat.finditer(s):
                            if (rep(m) if callable(rep) else m.expand(rep)) != m.group(0):
                                res["patterns"][name] += 1
                    for c, v in needles.items():
                        if v in s:
                            res["canaries"][c] += s.count(v)
    return res


def _pool_map(fn, args, jobs):
    """fn(*a) for each a, in order; in-process when jobs == 1."""
    if jobs <= 1:
        return [fn(*a) for a in args]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as ex:
        return list(ex.map(fn, *zip(*args))) if args else []


def gate(paths, jobs, extra=None):
    total = {"files": len(paths), "events": 0, "bad_lines": 0, "patterns": {}, "canaries": {}}
    for res in _pool_map(gate_file, [(p, extra) for p in paths], jobs):
        total["events"] += res["events"]
        total["bad_lines"] += res["bad_lines"]
        for k in ("patterns", "canaries"):
            for name, v in res[k].items():
                _inc(total[k], name, v)
    total["total"] = sum(total["patterns"].values()) + sum(total["canaries"].values())
    return total


def print_gate(g):
    print("gate: %d files, %d events, %d unreadable lines" % (g["files"], g["events"], g["bad_lines"]))
    for name, v in g["patterns"].items():
        print("pattern:%s %d" % (name, v))
    for name, v in g["canaries"].items():
        print("canary:%s %d" % (name, v))
    print("total %d" % g["total"])


def code_hashes():
    files = {os.path.join("scripts", f): sha256_file(os.path.join(HERE, f)) for f in ("session_export.py", "transcript_export.py")}
    return hashlib.sha256("".join("%s  %s\n" % (files[k], k) for k in sorted(files)).encode()).hexdigest(), files


def cmd_init_key(a):
    """G6: make the pseudonym key once: 32 random bytes, mode 0600, in a 0700 directory. An existing key is never
    replaced (its pseudonyms would stop joining across exports)."""
    os.makedirs(os.path.dirname(os.path.abspath(a.key)), mode=0o700, exist_ok=True)
    try:
        fd = os.open(a.key, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        print("session_export: %s exists; a key is made once and never replaced" % a.key, file=sys.stderr)
        return 2
    with os.fdopen(fd, "wb") as fh:
        fh.write(os.urandom(KEY_BYTES))
    print("created %s (%d bytes, mode 0600, key id %s)" % (a.key, KEY_BYTES, key_id(load_key(a.key))))
    return 0


def cmd_export(a):
    t0 = time.monotonic()
    export_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    root, out = os.path.abspath(a.root), os.path.abspath(a.out)
    try:
        key = load_key(a.key)
    except KeyRefused as e:
        print("session_export: %s" % e, file=sys.stderr)
        return 2
    if os.path.isdir(out) and os.listdir(out):
        print("session_export: out dir not empty: %s" % out, file=sys.stderr)
        return 2
    if a.offsets:
        with open(a.offsets) as fh:
            prior = json.load(fh)
        jobs_in = [(s["src"], s["offset"], s["input_sha256"]) for s in prior["sources"]]
        bad = [s for s, off, _ in jobs_in if not os.path.isfile(os.path.join(root, s)) or os.path.getsize(os.path.join(root, s)) < off]
        if bad:
            print("session_export: %d sources missing or shorter than their offsets" % len(bad), file=sys.stderr)
            return 2
        dirs, archives = prior["archive_dirs"], prior["archives"]
        if not all(archive_unchanged(x) for x in archives):
            print("session_export: a pruner archive changed or went missing since its offsets were fixed", file=sys.stderr)
            return 2
    else:
        srcs = sorted(os.path.relpath(p, root) for p in glob.glob(os.path.join(root, "*", "**", "*.jsonl"), recursive=True))
        jobs_in = [(s, fixed_offset(os.path.join(root, s)), None) for s in srcs]
        dirs = archive_dirs(root, [(s, off) for s, off, _ in jobs_in], a.archive_dir)
        archives = find_archives(dirs)
    if not jobs_in:
        print("session_export: no *.jsonl under %s" % root, file=sys.stderr)
        return 2
    os.makedirs(out, exist_ok=True)
    linked = {x["call_id"]: x for x in archives if x["call_id"]}
    order = sorted(jobs_in, key=lambda j: (-j[1], j[0]))                 # the largest first: it bounds the wall time
    results = _pool_map(export_source, [(root, s, off, out, sha, key, linked) for s, off, sha in order], a.jobs)
    errors = [r for r in results if "error" in r]
    if errors:
        for r in errors:
            print("session_export: %s: %s" % (r["src"], r["error"]), file=sys.stderr)
        return 2
    sources = sorted(results, key=lambda r: r["src"])
    g = gate([os.path.join(out, s["output"]) for s in sources], a.jobs, key_forms(key))
    emitted = {c for s in sources for c in s["archived"]}
    totals = {"sources": len(sources), "bytes_read": 0, "bytes_written": 0, "folders": {},
              "archives": len(archives), "archives_skipped": sum(1 for x in archives if x.get("skipped")),
              "archives_unlinked": sum(1 for x in archives if not x["call_id"] and not x.get("skipped")),
              "archives_unmatched": sum(1 for c in linked if c not in emitted)}
    for s in sources:
        totals["bytes_read"] += s["offset"]
        totals["bytes_written"] += s["output_bytes"]
        folder = totals["folders"].setdefault(s["src"].split("/", 1)[0], {"sources": 0, "bytes_read": 0})
        folder["sources"] += 1
        folder["bytes_read"] += s["offset"]
        for k in ("lines", "bad_lines", "seam_adjusted", "dropped_secret_path", "strict_results", "unsettled",
                  "thinking_signature_only", "duplicate_notifications", "file_changes_unrecorded", "pruner_archives",
                  "pseudonyms"):
            _inc(totals, k, s[k])
        for k in ("events", "capped", "skipped_records", "skipped_attachments"):
            for name, v in s[k].items():
                _inc(totals.setdefault(k, {}), name, v)
    for k in ("events", "capped", "skipped_records", "skipped_attachments"):
        totals[k] = dict(sorted(totals.get(k, {}).items()))
    code_sha, code = code_hashes()
    manifest = {"schema": 2, "export_id": export_id, "root": root, "code_sha256": code_sha, "code": code,
                "pseudonym_key_id": key_id(key),
                "limits": {"cap": CAP, "kept_head": HEAD, "kept_tail": TAIL, "big_cap": BIG_CAP, "big_kept_head": BIG_HEAD,
                           "big_kept_tail": BIG_TAIL, "xz_preset": XZ_PRESET},
                "archive_dirs": dirs, "archives": archives, "sources": sources, "totals": totals, "gate": g,
                "wall_seconds": round(time.monotonic() - t0, 1)}
    with open(os.path.join(out, "manifest.json.part"), "w") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    os.replace(os.path.join(out, "manifest.json.part"), os.path.join(out, "manifest.json"))
    print("export %s: %d sources, %d bytes read, %d bytes written, %.1f s" % (
        export_id, len(sources), totals["bytes_read"], totals["bytes_written"], manifest["wall_seconds"]))
    print("folders " + json.dumps(totals["folders"]))
    print("events " + json.dumps(totals["events"]))
    print("capped " + json.dumps(totals["capped"]))
    print(" ".join("%s %d" % (k, totals[k]) for k in (
        "dropped_secret_path", "strict_results", "unsettled", "seam_adjusted", "thinking_signature_only",
        "duplicate_notifications", "file_changes_unrecorded", "pseudonyms", "pruner_archives", "archives",
        "archives_skipped", "archives_unlinked", "archives_unmatched")))
    print_gate(g)
    return 3 if g["total"] or g["bad_lines"] else 0


def cmd_gate(a):
    paths = sorted(p for p in glob.glob(os.path.join(os.path.abspath(a.dir), "**", "*.xz"), recursive=True))
    if not paths:
        print("session_export: no *.xz under %s" % a.dir, file=sys.stderr)
        return 2
    extra = None
    if a.key:
        try:
            extra = key_forms(load_key(a.key))
        except KeyRefused as e:
            print("session_export: %s" % e, file=sys.stderr)
            return 2
    g = gate(paths, a.jobs, extra)
    print_gate(g)
    return 3 if g["total"] or g["bad_lines"] else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("init-key")
    k.add_argument("--key", default=KEY_PATH)
    e = sub.add_parser("export")
    e.add_argument("--out", required=True)
    e.add_argument("--root", default=PROJECTS)
    e.add_argument("--offsets")
    e.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    e.add_argument("--key", default=KEY_PATH)
    e.add_argument("--archive-dir", action="append", default=[])
    g = sub.add_parser("gate")
    g.add_argument("dir")
    g.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    g.add_argument("--key")
    a = ap.parse_args(argv)
    return {"init-key": cmd_init_key, "export": cmd_export, "gate": cmd_gate}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
