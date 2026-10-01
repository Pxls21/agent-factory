#!/usr/bin/env python3
"""render.py — the ONE render of an exported event stream into text (task #444, S3-5 in tasks/laya-s3-breakdown.md;
brief tasks/briefs/jev-laya/S3-5-VIEW-brief.md, D-1).

A frozen RWKV-7 reads each transcript's exported stream (scripts/session_export.py) once (D-125, D-126). The stream is
rendered as text, and three users render it the same way: view.py (where the state of each S1 injection ends), task
#441's reading pass (it finds each state's end in its own render) and task #448's live reader, which renders one event
at a time. So a block depends on its event alone.

block(event) is one event's block, "<label>: <body>" and a blank line, or "" (LABELS; any other (role, kind) raises
UnknownPair). The body, in order: transcript_export.scrub_payload (no opaque callable; counted scrub_changed
when it changed the text); CR LF and CR to LF; every run of two or more LF to one LF (the blank line separates blocks);
strip; an empty body gives ""; over CAP characters, the first HEAD, the cut mark, then the last TAIL (counted cut).

A hook event's body is what the hook handed the model: its text parsed as JSON; an attachment whose type starts with
`hook_` gives the texts s1_scores.injections_of returns for it, joined by LF (an additional context; a hook_success's
content only for s1_scores.PLAIN_EVENTS; a blocking error's message; nothing else); any other JSON gives nothing; a text
that is not JSON gives itself when it is `Stop hook feedback:` text (the exporter's own test, after lstrip) and nothing
otherwise (counted hook_unparsed). A thinking block never renders.

render(events) -> (text, starts) takes the events of ONE export file in file order; starts[i] is the offset in `text` (a
str index: code points) where event i's block begins, the length of every block before it, so it is defined for an
event that renders nothing. `counts`, when given, is a dict that takes scrub_changed, cut and hook_unparsed.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # scripts/: s1_scores, transcript_export
import s1_scores as S  # noqa: E402  the ONE reading of what a hook handed the model
from transcript_export import scrub_payload  # noqa: E402

VERSION = "s1-render-v1"
CAP, HEAD, TAIL = 4000, 3000, 1000          # characters of a body, after the scrub and the newline rule
CUT_MARK = "\n[... %d characters cut ...]\n"  # %d: the body's length minus CAP
FEEDBACK = "Stop hook feedback:"
# (role, kind) -> its label (`%s`: the event's tool, `?` when it has none), or None: the pair renders nothing (thinking,
# and the harness's own records the export keeps for the record). Any other pair is refused (UnknownPair).
LABELS = {("owner", "text"): "Owner", ("coordinator", "text"): "Coordinator", ("agent", "text"): "Agent",
          ("coordinator", "tool_call"): "Coordinator calls %s", ("agent", "tool_call"): "Agent calls %s",
          ("tool", "tool_result"): "Result of %s", ("hook", "hook"): "Hook", ("system", "summary"): "Summary",
          ("coordinator", "thinking"): None, ("agent", "thinking"): None, ("system", "notification"): None,
          ("system", "harness_notice"): None, ("system", "api_error"): None, ("tool", "file_change"): None,
          ("tool", "pruner_archive"): None}
NEWLINE_RUN = re.compile(r"\n{2,}")


class UnknownPair(ValueError):
    """An event whose (role, kind) the table does not hold: refused, never guessed."""


def _count(counts, key):
    if counts is not None:
        counts[key] = counts.get(key, 0) + 1


def newlines(text):
    """CR LF and CR to LF, then every run of two or more LF to one LF."""
    return NEWLINE_RUN.sub("\n", text.replace("\r\n", "\n").replace("\r", "\n"))


def clean(text, counts=None):
    """The body rules without the cap: the scrub, the newline rule, strip."""
    out = scrub_payload(text)
    if out != text:
        _count(counts, "scrub_changed")
    return newlines(out).strip()


def body(text, counts=None):
    """clean(), then the cap: a body over CAP characters keeps its first HEAD and its last TAIL around the cut mark."""
    out = clean(text, counts)
    if len(out) > CAP:
        _count(counts, "cut")
        out = out[:HEAD] + CUT_MARK % (len(out) - CAP) + out[-TAIL:]
    return out


def injections(a):
    """s1_scores.injections_of for `a`, the JSON a hook event's text holds, when it is an attachment whose type starts
    with `hook_`; [] for any other JSON (a stop-hook summary's type is `system`)."""
    if isinstance(a, dict) and isinstance(a.get("type"), str) and a["type"].startswith("hook_"):
        return S.injections_of({"type": "attachment", "attachment": a})
    return []


def hook_text(text, counts=None):
    """What a hook event handed the model, before the body rules."""
    try:
        a = json.loads(text)
    except ValueError:
        if text.lstrip().startswith(FEEDBACK):
            return text
        _count(counts, "hook_unparsed")
        return ""
    return "\n".join(t for _kind, _event, _tool, t, _cmd in injections(a))


def block(event, counts=None):
    """One event's block: "<label>: <body>" and a blank line, or "" (a silent pair or an empty body)."""
    pair = (event.get("role"), event.get("kind"))
    if pair not in LABELS:
        raise UnknownPair("unknown (role, kind) %r" % (pair,))
    label = LABELS[pair]
    if label is None:
        return ""
    text = hook_text(event["text"], counts) if pair == ("hook", "hook") else event["text"]
    out = body(text, counts)
    if not out:
        return ""
    if "%s" in label:
        label = label % (event["tool"] if isinstance(event.get("tool"), str) else "?")
    return "%s: %s\n\n" % (label, out)


def render(events, counts=None):
    """(text, starts) of one export file's events, in file order."""
    parts, starts, at = [], [], 0
    for ev in events:
        starts.append(at)
        b = block(ev, counts)
        parts.append(b)
        at += len(b)
    return "".join(parts), starts
