#!/usr/bin/env python3
"""K1-COMPACTION-LOSS (task #352, D-106), rounds 1 and 2: what does a compaction lose, and does the work get worse as
the context fills?

    compaction.py select --transcript MAIN --subagents DIR --sizes SIZES.json --out DIR
    compaction.py run --transcript FILE --pin BYTES --label NAME --out DIR [--sidechain] [--shapes v1|v2]
    compaction.py summary --out DIR [--stamp STAMP]

The briefs are tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md (round 1) and K1-R2-brief.md (round 2, a contract
amendment after tasks/briefs/jev-trim/VERIFY-K1-report.md); the plan is docs/research/findings/jev-trim/
D105-DESIGN-v1.md §10.2 (R-B, R-C). It measures and recommends nothing. It imports scripts/jev_trim/replay.py (the
timeline: requests, segments opened by compact_boundary records, items with modeled sizes and P1 tokens) and
scripts/jev_pipes (the walker and accounting.miss) and modifies neither.

SHAPE SETS (`run --shapes`, default v1). v1 is round 1's measurement unchanged: its outputs
(docs/research/findings/jev-trim/compaction-2026-09-29/) re-generate byte for byte. v2 is round 2's
(compaction-2026-09-29-r2/): the parts marked v2 below. compaction_loss() called without a shape set applies v2.

PINS (`select`): the main transcript, and every subagent transcript holding at least one compact_boundary record (a
parsed system record, never a text match), each at the size measured at the lane's start (--sizes), stepped back to a
record boundary. A subagent file that holds a boundary now but was not measured at the start is listed as not pinned.
A `run --pin` beyond the file's size stops with PinBeyondFileSize.

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

R-C v2 (round 2; VERIFY-K1's F2 and F3).
- Direction: each window call is a read, a write, a commit, a script or other (DIRECTION below). A search_* shape
  counts a call only when it is neither a write nor a commit (VERIFY-K1's "writes out"); each call a search shape
  matches is reported by direction, per shape, and a write or a commit enters no total.
- The strict shapes, tried on a call no K1 shape counted, added to refetch_total (K1's shapes alone are k1_total): (a)
  bash_view_known_file, a `cat`, `sed`, `head`, `tail`, `nl`, `less` or `awk` view of a file the pre segment Read,
  edited or viewed through Bash; (b) read_bash_viewed_file, a Read of a file the pre segment viewed through Bash; (c)
  git_repeated_args, a `git log`, `show`, `diff` or `blame` with the subcommand and non-flag arguments of one in the pre
  segment; (d) read_known_path_respelled, a Read of a file the pre segment Read or edited, spelled another way. Two
  names name one file when they are equal after `./` and `//` are folded, or one is relative and ends the other,
  absolute one at a `/` (K1's rule for a missed path, both ways).
- The loose shapes, tried after them, their own total (loose_total; with_loose_total adds it to refetch_total), never
  in refetch_total: grep_known_token, the Grep tool, `grep`, `egrep`, `fgrep`, `rg` or `graft ask` whose pattern holds an
  accounting token of the pre segment; git_any, any `git log`, `show` or `diff`.
- Windows: 20, 20-99 (requests 20 to 99 only), 100 and the rest.
- Controls: points with no compaction; a point's history is its segment before it (K1's rule) and nothing is removed,
  so its miss is 0. C1 as round 1. C2, paired: for each boundary whose pre segment holds 2 x PSEUDO_GAP requests or
  more, the point PSEUDO_GAP requests before its end; its windows run to the compaction and count the final request's
  outputs (replay.build drops the items a segment's last request produced; timeline() keeps them). C5, sliding: every
  C5_STEP requests from request C5_START of every segment, a window counted only when the segment holds it whole (no
  rest window).
- The summary: per window and control, the rate per 100 requests (the calls over the requests, summed over the points),
  the excess (the real rate minus the control's) and its 95% percentile bootstrap interval (BOOTSTRAP replicates;
  boundaries and points resampled with replacement, C5 by segment; each interval seeded from sha256 of its cell's
  name, so a re-run writes the same bytes); the rates per shape and label; the search shapes by direction; the share
  of missed paths that name a file the pre segment read or edited.

DIRECTION (v2). An edit tool is a write; Read, Grep and Glob are reads; any other tool but Bash is other. A Bash
command is parsed: heredoc bodies dropped, line continuations and comments dropped outside quotes, then shlex (POSIX)
splits it into simple commands at `;`, `&`, `&&`, `|`, `||`, newlines and parentheses (on a quoting error, round 1's
whitespace split). A simple command is a write when it redirects output into a file other than /dev/null, runs
scripts/anchor_edit.py, or is `sed -i`, `tee` into a file, `cp` or `mv`; a commit when it runs scripts/safe_commit.sh or
scripts/push_clean.sh, or is `git commit`, `git add` or `git push`; a read when its program is in READ_PROGRAMS, a git
subcommand in GIT_READ or `graft ask`; a script when its program is an interpreter or a .py or .sh file; else other. A
command takes the first of write, commit, read, script and other that one of its simple commands is.

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
excess over the control. v2 adds a position-aware variant (POSITION_ASSUMPTIONS), the included requests' actual usage,
and the loss at the corrected counts over C1, C2 and C5, for both models.

Outputs carry counts, sizes, offsets, ids and tool, kind, rule, shape, label, direction, gate and model names only;
token sets live in memory and are never printed or stored.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import contextlib
import datetime
import functools
import hashlib
import json
import math
import os
import random
import re
import shlex
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

# ---------------------------------------------------------------- round 2 (v2)

SHAPE_SETS = ("v1", "v2")
WINDOWS_V2 = (("20", 0, 20), ("20-99", 20, 80), ("100", 0, 100), ("rest", 0, None))  # (label, first request, length)
C5_START, C5_STEP = 100, 20
BOOTSTRAP = 2000
POSITION_BUCKETS = (20, 100)  # positions 0-19, 20-99, and 100 and later
BUCKET_NAMES = ("0-19", "20-99", "100+")
CALIBRATION_STEPS = 40
SEARCH_SHAPES = ("search_transcript", "search_ledger", "search_live_state")
STRICT_LABELS = ("bash_view_known_file", "read_bash_viewed_file", "git_repeated_args", "read_known_path_respelled")
LOOSE_LABELS = ("grep_known_token", "git_any")
TOTALS = ("k1_total", "strict_total", "refetch_total", "loose_total", "with_loose_total")
DIRECTIONS = ("read", "script", "other", "write", "commit")
NOT_A_READ = frozenset({"write", "commit"})
READ_TOOLS = frozenset({"Read", "Grep", "Glob"})
VIEW_PROGRAMS = frozenset({"cat", "sed", "head", "tail", "nl", "less", "awk"})
GREP_PROGRAMS = frozenset({"grep", "egrep", "fgrep", "rg"})
READ_PROGRAMS = VIEW_PROGRAMS | GREP_PROGRAMS | frozenset({
    "wc", "ls", "find", "jq", "diff", "cmp", "stat", "file", "du", "more", "sort", "uniq", "cut", "sha256sum", "md5sum",
    "tac", "xxd", "od", "strings", "tree", "realpath", "readlink"})
GIT_READ = frozenset({"log", "show", "diff", "blame", "grep", "status", "ls-files", "cat-file", "rev-parse",
                      "merge-base", "shortlog", "reflog", "describe"})
GIT_STRICT = frozenset({"log", "show", "diff", "blame"})
GIT_LOOSE = frozenset({"log", "show", "diff"})
GIT_COMMIT = frozenset({"commit", "add", "push"})
INTERPRETERS = frozenset({"python", "python3", "bash", "sh", "zsh", "node", "uv", "perl", "ruby"})
WRITE_SCRIPTS = ("anchor_edit.py",)
COMMIT_SCRIPTS = ("safe_commit.sh", "push_clean.sh")
POSITION_ASSUMPTIONS = (
    "Position-aware variant: each observed step is scaled by g(its modeled bucket) / g(its observed bucket), g being "
    "the mean growth per request of the included segments' steps by position since the segment start (buckets 0-19, "
    "20-99, 100 and later; a step, request i's context minus request i-1's, takes position i-1, the request whose "
    "output it adds: VERIFY-K1's convention; a bucket with no step takes the nearest earlier bucket's mean). The "
    "modeled position counts the requests since the stream's start or the last modeled compaction; the step across "
    "an observed compaction stays 0.",
    "Calibration: one scale on every step, found by bisection (CALIBRATION_STEPS halvings, the scale nearest 1) so "
    "that the position-aware count at the last X (785k) equals the observed compactions among the included segments; "
    "the unscaled count is reported beside it. The flat model is not rescaled.",
    "Actual usage: the included segments' requests' cache_read_input_tokens, cache_creation_input_tokens and mean "
    "context from their first usage records; the session ran at about 785k, so only that X has an actual to compare.",
    "The corrected loss per compaction: the excess per boundary of K1's shapes (writes out) plus the strict set "
    "(refetch_total), and with the loose set (with_loose_total), over each control: (the real rate - the control's "
    "rate) x the real mean requests per boundary, times the modeled compactions.",
)


class PinBeyondFileSize(ValueError):
    """A run's --pin is beyond its transcript's size."""


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


# ---------------------------------------------------------------- the shell (v2)

_PUNCT = ";&|()<>\n"
_OPERATORS = ("&>>", "&>", ">>", ">|", ">&", "<<<", "<<", "<&", "<>", "||", "&&", "|&", ";;", ">", "<", "|", "&", ";",
              "(", ")", "\n")
_SEPARATORS = frozenset({"||", "&&", "|&", ";;", "|", "&", ";", "(", ")", "\n"})
_OUTPUTS = frozenset({"&>>", "&>", ">>", ">|", ">"})
_HEREDOC = re.compile(r"(?<!<)<<(?!<)(-?)[ \t]*\\?(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
_PYTHON = re.compile(r"python3?(?:\.\d+)?")
_WRAPPERS = frozenset({"sudo", "nohup", "time", "exec", "command", "env", "nice", "stdbuf"})
_RANK = {"other": 0, "script": 1, "read": 2, "commit": 3, "write": 4}
_TAKES = {  # a view's flags that take the next word as their value
    "cat": frozenset(), "less": frozenset(),
    "head": frozenset({"-n", "-c", "--lines", "--bytes"}),
    "tail": frozenset({"-n", "-c", "--lines", "--bytes", "-s", "--pid", "--sleep-interval"}),
    "nl": frozenset({"-b", "-d", "-f", "-h", "-i", "-l", "-n", "-s", "-v", "-w"}),
    "sed": frozenset({"-e", "-f", "-l", "--expression", "--file", "--line-length"}),
    "awk": frozenset({"-F", "-v", "-f", "--field-separator", "--assign", "--file"}),
}
_GREP_TAKES = frozenset({"-A", "-B", "-C", "-m", "-f", "-d", "-D", "-g", "-t", "-T", "-j", "-M", "--glob", "--type",
                         "--type-not", "--max-count", "--context", "--after-context", "--before-context", "--file",
                         "--threads", "--max-columns", "--include", "--exclude", "--exclude-dir"})


def _prepare(command: str) -> str:
    """The command with heredoc bodies dropped (line by line), then line continuations and comments dropped outside
    quotes: what shlex splits."""
    kept, waiting = [], []
    for line in command.split("\n"):
        if waiting:
            delimiter, tabs = waiting[0]
            if (line.lstrip("\t") if tabs else line).strip() == delimiter:
                waiting.pop(0)
            continue  # a heredoc body line, or its end
        kept.append(line)
        waiting.extend((m.group(3), m.group(1) == "-") for m in _HEREDOC.finditer(line))
    text, out, quote, prev, i = "\n".join(kept), [], None, "\n", 0
    while i < len(text):
        ch = text[i]
        if quote == "'":
            quote = None if ch == "'" else quote
        elif ch == "\\" and i + 1 < len(text):
            if text[i + 1] != "\n":  # a backslash-newline is a line continuation: both go
                out.append(text[i:i + 2])
                prev = text[i + 1]
            i += 2
            continue
        elif quote == '"':
            quote = None if ch == '"' else quote
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and prev in " \t\n;&|()":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        out.append(ch)
        prev = ch
        i += 1
    return "".join(out)


def _operators(run: str) -> list:
    out, i = [], 0
    while i < len(run):
        op = next((o for o in _OPERATORS if run.startswith(o, i)), run[i])
        out.append(op)
        i += len(op)
    return out


def _argv(words: list) -> tuple:
    """The words after leading assignments and wrappers (sudo, nohup, time, env, timeout DURATION ...)."""
    i = 0
    while i < len(words):
        word = words[i]
        if _ASSIGNMENT.match(word):
            i += 1
        elif word in _WRAPPERS or word == "timeout":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 1
            if word == "timeout":
                i += 1  # its duration
        else:
            break
    return tuple(words[i:])


def _simple_commands(command: str) -> tuple:
    """((argv, output redirect targets), ...): the simple commands of a Bash command."""
    text = _prepare(command)
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=_PUNCT)
        lex.whitespace, lex.whitespace_split, lex.commenters = " \t\r", True, ""
        tokens = list(lex)
    except ValueError:  # an unbalanced quote: round 1's rule, a whitespace split
        tokens = text.split()
    commands, words, targets, pending = [], [], [], None
    for token in tokens + ["\n"]:
        if token and all(c in _PUNCT for c in token):
            for op in _operators(token):
                if op in _SEPARATORS:
                    argv = _argv(words)
                    if argv or targets:
                        commands.append((argv, tuple(targets)))
                    words, targets, pending = [], [], None
                else:
                    if words and words[-1].isdigit():
                        words.pop()  # a descriptor: the 2 of 2>
                    pending = op
            continue
        if pending is not None:
            if pending in _OUTPUTS or (pending == ">&" and not (token.isdigit() or token == "-")):
                targets.append(token)
            pending = None
            continue
        words.append(token)
    return tuple(commands)


def _base(word: str) -> str:
    return word.rsplit("/", 1)[-1]


def _script_of(argv: tuple) -> str:
    """The script a simple command runs: an interpreter's first operand, else its program."""
    prog = _base(argv[0])
    if prog in INTERPRETERS or _PYTHON.fullmatch(prog):
        return next((w for w in argv[1:] if not w.startswith("-")), "")
    return argv[0]


def _in_place(argv: tuple) -> bool:
    return any(w == "--in-place" or w.startswith("--in-place=") or (w[:1] == "-" and w[1:2] != "-" and "i" in w[1:])
               for w in argv[1:])


def _git_key(argv: tuple) -> tuple | None:
    """(subcommand, non-flag arguments) of a git command, or None."""
    if not argv or _base(argv[0]) != "git":
        return None
    i = 1
    while i < len(argv) and argv[i].startswith("-"):
        i += 2 if argv[i] in ("-C", "-c") else 1
    if i >= len(argv):
        return None
    args, positional = [], False
    for word in argv[i + 1:]:
        if positional or not word.startswith("-"):
            args.append(word)
        elif word == "--":
            positional = True
    return argv[i], tuple(args)


def _simple_direction(argv: tuple, targets: tuple) -> str:
    if any(t != "/dev/null" for t in targets):
        return "write"
    if not argv:
        return "other"
    prog, script = _base(argv[0]), _script_of(argv)
    if (script.endswith(WRITE_SCRIPTS) or prog in ("cp", "mv") or (prog == "sed" and _in_place(argv))
            or (prog == "tee" and any(w != "/dev/null" and not w.startswith("-") for w in argv[1:]))):
        return "write"
    if script.endswith(COMMIT_SCRIPTS):
        return "commit"
    if prog == "git":
        sub = (_git_key(argv) or (None,))[0]
        return "commit" if sub in GIT_COMMIT else ("read" if sub in GIT_READ else "other")
    if prog in READ_PROGRAMS or (prog == "graft" and argv[1:2] == ("ask",)):
        return "read"
    if prog in INTERPRETERS or _PYTHON.fullmatch(prog) or prog.endswith((".py", ".sh")):
        return "script"
    return "other"


@functools.lru_cache(maxsize=None)
def _bash(command: str) -> tuple:
    """(the simple commands, the command's direction)."""
    commands = _simple_commands(command)
    direction = max((_simple_direction(argv, targets) for argv, targets in commands), key=_RANK.__getitem__,
                    default="other")
    return commands, direction


def _is_view(argv: tuple) -> bool:
    return bool(argv) and _base(argv[0]) in VIEW_PROGRAMS and not (_base(argv[0]) == "sed" and _in_place(argv))


def _view_files(argv: tuple) -> list:
    """A view's file operands: its flags' values and a sed or awk program (unless a flag gave it) are skipped."""
    prog = _base(argv[0])
    takes, program = _TAKES[prog], prog in ("sed", "awk")
    files, i, positional = [], 1, False
    while i < len(argv):
        word = argv[i]
        i += 1
        if not positional and word == "--":
            positional = True
            continue
        if not positional and word.startswith("-") and word != "-":
            short = word[1:2] != "-"
            cluster = short and prog == "sed" and word[-1] in "ef"  # -ne SCRIPT, -nf FILE
            if word in ("-e", "-f", "--expression", "--file") or cluster or (short and prog == "awk"
                                                                             and word.startswith("-f")):
                program = False
            if word in takes or cluster:
                i += 1  # the flag's value
            continue
        if program:
            program = False
            continue
        if prog == "awk" and _ASSIGNMENT.match(word):
            continue
        if word not in ("-", "/dev/null", "/dev/stdin"):
            files.append(word)
    return files


def _search_patterns(argv: tuple) -> list:
    """A grep, egrep, fgrep or rg's patterns (its -e values, else its first operand), or a `graft ask` question."""
    if not argv:
        return []  # a redirect alone: `> file`
    prog = _base(argv[0])
    if prog == "graft":
        question = next((w for w in argv[2:] if not w.startswith("-")), "") if argv[1:2] == ("ask",) else ""
        return [question] if question else []
    if prog not in GREP_PROGRAMS:
        return []
    explicit, first, i, positional = [], None, 1, False
    while i < len(argv):
        word = argv[i]
        i += 1
        if not positional and word == "--":
            positional = True
        elif not positional and word in ("-e", "--regexp"):
            explicit += list(argv[i:i + 1])
            i += 1
        elif not positional and word.startswith("--regexp="):
            explicit.append(word.split("=", 1)[1])
        elif not positional and word.startswith("-") and word != "-":
            i += 1 if word in _GREP_TAKES else 0
        elif first is None:
            first = word
    return explicit or ([first] if first is not None else [])


def _norm(path: str) -> str:
    """A file name with `./` and `//` folded and no trailing `/`."""
    name = path.strip()
    while name.startswith("./"):
        name = name[2:]
    name = re.sub(r"/(?:\./)+", "/", name)
    name = re.sub(r"/{2,}", "/", name)
    return name[:-1] if len(name) > 1 and name.endswith("/") else name


def _same_file(a: str, b: str) -> bool:
    """Two folded names name one file: equal, or one relative and ending the other, absolute one at a `/`."""
    if a == b:
        return True
    if a.startswith("/") != b.startswith("/"):
        absolute, relative = (a, b) if a.startswith("/") else (b, a)
        return absolute.endswith("/" + relative)
    return False


class _Files:
    """File names by their last part; has() says whether a name names one of them (_same_file)."""

    def __init__(self, paths) -> None:
        self.by_name: dict = collections.defaultdict(set)
        for path in paths:
            name = _norm(path)
            if name:
                self.by_name[name.rsplit("/", 1)[-1]].add(name)

    def has(self, path: str) -> bool:
        name = _norm(path)
        return any(_same_file(name, known) for known in self.by_name.get(name.rsplit("/", 1)[-1], ()))


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
    viewed: set = field(default_factory=set)  # v2: the files Bash views named
    git: set = field(default_factory=set)  # v2: (subcommand, non-flag arguments) of git log, show, diff and blame
    known_files: _Files | None = None  # v2: read, edited or viewed
    viewed_files: _Files | None = None  # v2
    read_or_edited: _Files | None = None  # v2


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


def _command_of(item: replay.Item) -> str:
    command = _call_input(item).get("command")
    return command if isinstance(command, str) else ""


def _note_bash(out: Facts, command: str) -> None:
    for argv, _ in _bash(command)[0]:
        if _is_view(argv):
            out.viewed.update(_view_files(argv))
        git = _git_key(argv)
        if git is not None and git[0] in GIT_STRICT:
            out.git.add(git)


def facts(items: list, v2: bool = False) -> Facts:
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
            if v2:
                _note_bash(out, _command_of(it))
        elif it.rerun is not None:
            out.calls.add(it.rerun)
    out.tokens = frozenset(tokens)
    if v2:
        out.known_files = _Files(out.reads | out.edits | out.viewed)
        out.viewed_files = _Files(out.viewed)
        out.read_or_edited = _Files(out.reads | out.edits)
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


def _direction(item: replay.Item) -> str:
    """v2: read, write, commit, script or other (DIRECTION in the docstring)."""
    if item.name in EDIT_TOOLS:
        return "write"
    if item.name in READ_TOOLS:
        return "read"
    if item.name != "Bash":
        return "other"
    return _bash(_command_of(item))[1]


def _strict_label(item: replay.Item, pre: Facts) -> str | None:
    """v2: the strict shape of a call no K1 shape counted, or None."""
    if item.name == "Read":
        path = _file_of(item)
        if path and pre.viewed_files.has(path):
            return "read_bash_viewed_file"
        if path and pre.read_or_edited.has(path):
            return "read_known_path_respelled"
        return None
    if item.name != "Bash":
        return None
    commands = _bash(_command_of(item))[0]
    for argv, _ in commands:
        if _is_view(argv) and any(pre.known_files.has(f) for f in _view_files(argv)):
            return "bash_view_known_file"
    for argv, _ in commands:
        git = _git_key(argv)
        if git is not None and git[0] in GIT_STRICT and git in pre.git:
            return "git_repeated_args"
    return None


def _loose_label(item: replay.Item, pre: Facts) -> str | None:
    """v2: the loose shape of a call neither a K1 nor a strict shape counted, or None."""
    patterns, commands = [], ()
    if item.name == "Grep":
        pattern = _call_input(item).get("pattern")
        patterns = [pattern] if isinstance(pattern, str) else []
    elif item.name == "Bash":
        commands = _bash(_command_of(item))[0]
        for argv, _ in commands:
            patterns += _search_patterns(argv)
    if any(accounting.tokens(p) & pre.tokens for p in patterns):
        return "grep_known_token"
    for argv, _ in commands:
        git = _git_key(argv)
        if git is not None and git[0] in GIT_LOOSE:
            return "git_any"
    return None


def _cost(item: replay.Item, results: dict) -> float:
    return item.size + (results[item.tool_use_id].size if item.tool_use_id in results else 0.0)


def _row(row: dict) -> dict:
    return {"calls": row["calls"], "tokens": round(row["tokens"], 1), "requests": len(row["requests"])}


def _total(rows: list) -> dict:
    return {"calls": sum(r["calls"] for r in rows), "tokens": round(math.fsum(r["tokens"] for r in rows), 1),
            "requests": len(set().union(*(r["requests"] for r in rows)))}


class _Tally:
    """v2, over one window: the direction of each call a search shape matched, and the strict and loose labels."""

    def __init__(self) -> None:
        self.directions = {s: collections.Counter() for s in SEARCH_SHAPES}
        self.labels = {label: {"calls": 0, "tokens": 0.0, "requests": set()} for label in STRICT_LABELS + LOOSE_LABELS}

    def take(self, it: replay.Item, shape: str | None, pre: Facts, results: dict, producer) -> str | None:
        """The K1 shape the call counts under, or None (a write or a commit, or a strict or loose label)."""
        direction = _direction(it)
        if shape in self.directions:
            self.directions[shape][direction] += 1
            if direction in NOT_A_READ:
                return None  # a search counts reads only (F2)
        if shape is not None:
            return shape
        if direction in NOT_A_READ:
            return None
        label = _strict_label(it, pre) or _loose_label(it, pre)
        if label is not None:
            row = self.labels[label]
            row["calls"] += 1
            row["tokens"] += _cost(it, results)
            row["requests"].add(producer(it))
        return None

    def dump(self, shapes: dict) -> dict:
        k1 = list(shapes.values())
        strict = [self.labels[label] for label in STRICT_LABELS]
        loose = [self.labels[label] for label in LOOSE_LABELS]
        return {"directions": {s: {d: self.directions[s][d] for d in DIRECTIONS} for s in SEARCH_SHAPES},
                "strict": {label: _row(self.labels[label]) for label in STRICT_LABELS},
                "loose": {label: _row(self.labels[label]) for label in LOOSE_LABELS},
                "k1_total": _total(k1), "strict_total": _total(strict),
                "refetch_total": _total(k1 + strict),
                "loose_total": _total(loose), "with_loose_total": _total(k1 + strict + loose)}


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
            results: dict, producer, reinjected: set, texts: tuple[str, str] | None = None,
            shape_set: str = "v1") -> dict:
    """One boundary (or pseudo-boundary) and one window: the miss, the reuse, the missed paths, the re-fetches (v2:
    reads apart from writes, the strict and loose shapes and their totals)."""
    used = frozenset().union(*(it.toks for it in look)) if look else frozenset()
    missed = _miss(original, kept, history, used, texts)
    paths = [t for t in missed if "/" in t and accounting._PATH.fullmatch(t)]
    edited = sum(1 for t in paths if _names_file(t, pre.edits))
    read = sum(1 for t in paths if not _names_file(t, pre.edits) and _names_file(t, pre.reads))
    shapes: dict = {s: {"calls": 0, "tokens": 0.0, "requests": set()} for s in SHAPES}
    tally = _Tally() if shape_set == "v2" else None
    reinjected_reads = 0
    for it in calls:
        shape = _shape(it, pre)
        if tally is not None:
            shape = tally.take(it, shape, pre, results, producer)
        if shape is None:
            continue
        row = shapes[shape]
        row["calls"] += 1
        row["tokens"] += it.size + (results[it.tool_use_id].size if it.tool_use_id in results else 0.0)
        row["requests"].add(producer(it))
        if shape == "read_known_path" and _file_of(it) in reinjected:
            reinjected_reads += 1
    all_requests = set().union(*(row["requests"] for row in shapes.values()))
    out = {"used": len(used), "reused": len((original - history) & used), "missed": len(missed),
           "missed_paths": len(paths), "missed_paths_edited_before": edited, "missed_paths_read_before": read,
           "missed_paths_neither": len(paths) - edited - read,
           "refetch": {s: {"calls": row["calls"], "tokens": round(row["tokens"], 1), "requests": len(row["requests"])}
                       for s, row in shapes.items()},
           "refetch_total": {"calls": sum(row["calls"] for row in shapes.values()),
                             "tokens": round(math.fsum(row["tokens"] for row in shapes.values()), 1),
                             "requests": len(all_requests)},
           "read_known_path_reinjected": reinjected_reads}
    if tally is not None:
        out.update(tally.dump(shapes))
    return out


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


def _span(segment: replay.Segment, pos: int, skip: int, n: int | None) -> tuple[list, list, int]:
    """v2: _window from request pos + skip; empty when the segment ends first."""
    if pos + skip >= len(segment.requests):
        return [], [], 0
    return _window(segment, pos + skip, n)


def _producer(segment: replay.Segment):
    offsets = [r.offset for r in segment.requests]
    return lambda it: bisect.bisect_right(offsets, it.offset) - 1


def _label(n: int | None) -> str:
    return "rest" if n is None else str(n)


def _post_tokens(segment: replay.Segment) -> int | None:
    value = segment.fixed_estimates.get("first_context_minus_post_tokens")
    return None if value is None else round(segment.requests[0].context - value)


def compaction_loss(tl: replay.Timeline, shape_set: str = "v2", tails: dict | None = None) -> dict:
    """R-C at every boundary with requests on both sides, and the control at the pseudo-boundaries (v2: C2 and C5
    too). `tails` (timeline()'s second value) holds the items replay.build drops after each segment's last request."""
    if shape_set not in SHAPE_SETS:
        raise ValueError(f"shape_set must be one of {SHAPE_SETS}, not {shape_set!r}")
    v2 = shape_set == "v2"
    by_index = {s.index: s for s in tl.segments}
    rows, skipped, pairs = [], [], []
    for k, (offset, day) in enumerate(tl.boundaries, start=1):
        pre, post = by_index.get(k - 1), by_index.get(k)
        if pre is None or post is None:
            skipped.append({"boundary": k, "offset": offset, "pre_has_requests": pre is not None,
                            "post_has_requests": post is not None})
            continue
        opening = [it for it in post.items if it.start]
        pre_facts, kept = facts(pre.items, v2), facts(opening)
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
                                                                 texts if n is None else None, shape_set)}
        if v2:
            look, calls, length = _span(post, 0, 20, 80)
            windows["20-99"] = {"requests": length, **measure(pre_facts.tokens, kept.tokens, post.fixed, look, calls,
                                                              pre_facts, results, producer, reinjected, None, "v2")}
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
        pairs.append((rows[-1], pre))
    control = []
    for segment in tl.segments:
        n = len(segment.requests)
        if n < 2 * PSEUDO_GAP:
            continue
        mid = n // 2
        split = segment.requests[mid].offset
        before = [it for it in segment.items if it.offset < split]
        pre_facts = facts(before, v2)
        results = {it.tool_use_id: it for it in segment.items if it.kind == "tool_result" and it.tool_use_id}
        producer = _producer(segment)
        windows = {}
        for w in WINDOWS:
            look, calls, length = _window(segment, mid, w)
            # nothing was removed: kept = everything still in context = the same items as the original
            windows[_label(w)] = {"requests": length, **measure(pre_facts.tokens, pre_facts.tokens, segment.fixed, look,
                                                                calls, pre_facts, results, producer, set(), None,
                                                                shape_set)}
        if v2:
            look, calls, length = _span(segment, mid, 20, 80)
            everything = pre_facts.tokens  # nothing removed, as above
            windows["20-99"] = {"requests": length, **measure(everything, everything, segment.fixed, look, calls,
                                                              pre_facts, results, producer, set(), None, "v2")}
        control.append({"segment": segment.index, "requests": n, "position": mid, "offset": split,
                        "class": _segment_class(tl, segment), "windows": windows})
    out = {"boundaries": rows, "skipped": skipped, "control": control}
    if v2:
        out.update({"shape_set": "v2", "control_c2": _paired(pairs, tails or {}), "control_c5": _sliding(tl)})
    return out


def _control_point(segment: replay.Segment, pos: int, results: dict, tail: list, whole: bool) -> dict:
    """v2: a point with no compaction at request `pos` (C2, C5): its history is the segment before it and nothing is
    removed. `tail` joins a window that reaches the segment's end; `whole` keeps only whole windows (C5)."""
    n = len(segment.requests)
    cut = segment.requests[pos].offset
    history = facts([it for it in segment.items if it.offset < cut], True)
    producer = _producer(segment)
    windows = {}
    for label, skip, length in WINDOWS_V2:
        if whole and (length is None or pos + skip + length > n):
            continue  # C5 counts whole windows only
        look, calls, count = _span(segment, pos, skip, length)
        if count and (length is None or pos + skip + length >= n):  # the window reaches the segment's end
            look = look + [it for it in tail if it.kind in LOOK_KINDS]
            calls = calls + [it for it in tail if it.kind == "tool_input"]
        windows[label] = {"requests": count, **measure(history.tokens, history.tokens, segment.fixed, look, calls,
                                                       history, results, producer, set(), None, "v2")}
    return {"position": pos, "offset": cut, "windows": windows}


def _paired(pairs: list, tails: dict) -> list:
    """C2: per boundary whose pre segment holds 2 x PSEUDO_GAP requests or more, the point PSEUDO_GAP requests before
    the compaction; its windows reach the compaction with the final request's outputs (the tail) counted."""
    points = []
    for row, pre in pairs:
        if len(pre.requests) < 2 * PSEUDO_GAP:
            continue
        tail = tails.get(pre.index, [])
        results = {it.tool_use_id: it for it in pre.items + tail if it.kind == "tool_result" and it.tool_use_id}
        point = _control_point(pre, len(pre.requests) - PSEUDO_GAP, results, tail, False)
        points.append({"boundary": row["boundary"], "segment": pre.index, "requests": len(pre.requests),
                       "class": row["class"], "tail_calls": sum(1 for it in tail if it.kind == "tool_input"), **point})
    return points


def _sliding(tl: replay.Timeline) -> list:
    """C5: every C5_STEP requests from request C5_START of every segment, whole windows only."""
    points = []
    for segment in tl.segments:
        n = len(segment.requests)
        positions = range(C5_START, n - C5_STEP + 1, C5_STEP)
        if not positions:
            continue
        cls = _segment_class(tl, segment)
        results = {it.tool_use_id: it for it in segment.items if it.kind == "tool_result" and it.tool_use_id}
        for pos in positions:
            points.append({"segment": segment.index, "requests": n, "class": cls,
                           **_control_point(segment, pos, results, [], True)})
    return points


def _ends_in_compaction(tl: replay.Timeline, segment: replay.Segment) -> bool:
    last = segment.requests[-1].offset
    return any(offset > last for offset, _ in tl.boundaries)


def _segment_class(tl: replay.Timeline, segment: replay.Segment) -> str:
    small = _ends_in_compaction(tl, segment) and segment.requests[-1].context < CLASS_SPLIT
    return "200k_window" if small else "1M_window"


@contextlib.contextmanager
def _tails_kept(out: dict):
    """While open, replay.build keeps in `out`, per segment, the items it drops after the segment's last request (their
    tokens computed here). replay.py is read-only: the wrapper calls its _segments unchanged and returns the same
    segments."""
    original = replay._segments

    def keep(requests, items, *rest):
        segments = original(requests, items, *rest)
        last = {s.index: s.requests[-1].offset for s in segments}
        tail = [it for it in items if it.seg in last and it.offset >= last[it.seg]]
        for it in sorted(tail, key=lambda it: (it.offset, it.sub)):
            if it.text is not None:
                it.toks = accounting.tokens(it.text)
            out.setdefault(it.seg, []).append(it)
        return segments

    replay._segments = keep
    try:
        yield out
    finally:
        replay._segments = original


def timeline(path: str, pin: int, sidechain: bool, shape_set: str = "v2") -> tuple:
    """(the replay timeline, the items after each segment's last request: v2 only, else None)."""
    if shape_set == "v1":
        return replay.build(path, pin, sidechain=sidechain), None
    tails: dict = {}
    with _tails_kept(tails):
        tl = replay.build(path, pin, sidechain=sidechain)
    return tl, tails


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


def _controls(rc: dict, cls: str) -> dict:
    return {"C1": [p for p in rc["control"] if p["class"] == cls],
            "C2": [p for p in rc.get("control_c2", []) if p["class"] == cls],
            "C5": [p for p in rc.get("control_c5", []) if p["class"] == cls]}


def _loss_means_v2(rc: dict, cls: str = "1M_window") -> dict:
    """v2, per window and total (refetch_total, with_loose_total): the real mean per boundary, and the excess per
    boundary over each control: (the real rate - the control's rate) x the real mean requests per boundary."""
    real = [r for r in rc["boundaries"] if r["class"] == cls]
    controls = _controls(rc, cls)
    out = {}
    for label, _, _ in WINDOWS_V2:
        ws = [r["windows"][label] for r in real]
        requests = sum(w["requests"] for w in ws)
        entry: dict = {"boundaries": len(ws), "requests_per_boundary": round(requests / len(ws), 3) if ws else None}
        for key in ("refetch_total", "with_loose_total"):
            if not ws or not requests:
                entry[key] = None
                continue
            calls, tokens = sum(w[key]["calls"] for w in ws), math.fsum(w[key]["tokens"] for w in ws)
            cell: dict = {"real": {"calls": round(calls / len(ws), 4), "tokens": round(tokens / len(ws), 1)}}
            for name, points in controls.items():
                cs = [p["windows"][label] for p in points if label in p["windows"]]
                c_requests = sum(w["requests"] for w in cs)
                if not c_requests:
                    cell[name] = None
                    continue
                c_calls, c_tokens = sum(w[key]["calls"] for w in cs), math.fsum(w[key]["tokens"] for w in cs)
                per = requests / len(ws)
                cell[name] = {"calls": round((calls / requests - c_calls / c_requests) * per, 4),
                              "tokens": round((tokens / requests - c_tokens / c_requests) * per, 1)}
            entry[key] = cell
        out[label] = entry
    return out


def _scaled(means: dict, compactions: int) -> dict:
    """v2: a model row's corrected loss: every per-boundary value of _loss_means_v2 times the compactions."""
    out = {}
    for label, entry in means.items():
        out[label] = {}
        for key in ("refetch_total", "with_loose_total"):
            cell = entry[key]
            out[label][key] = None if cell is None else {
                name: (None if value is None else {k: round(v * compactions, 1) for k, v in value.items()})
                for name, value in cell.items()}
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


def _bucket(position: int) -> int:
    return bisect.bisect_right(POSITION_BUCKETS, position)


def growth_means(steps: list[float], positions: list[int]) -> list:
    """v2: the mean growth per request in each position bucket, over the steps inside a segment (a step across an
    observed compaction has position -1 and is left out); a bucket with no step takes the nearest earlier bucket's
    mean (None when the first has none)."""
    values: list = [[] for _ in BUCKET_NAMES]
    for step, position in zip(steps, positions):
        if position >= 0:
            values[_bucket(position)].append(step)
    means, last = [], None
    for bucket in values:
        last = math.fsum(bucket) / len(bucket) if bucket else last
        means.append(last)
    return means


def simulate_positions(steps: list[float], positions: list[int], kept: float, point: float, means: list,
                       scale: float = 1.0) -> dict:
    """v2, the position-aware model at `point` (POSITION_ASSUMPTIONS): a step grows by scale x step x the mean growth
    of its modeled position's bucket over its observed one's (a step takes the position of the request it leaves); a
    modeled compaction resets the modeled position."""
    fill, m = float(kept), 0  # m: the position of the request the stream is at
    total, reads, writes, summarizer = fill, 0.0, fill, 0.0
    compactions = 0
    for step, position in zip(steps, positions):
        grown = scale * step * means[_bucket(m)] / means[_bucket(position)]
        if fill + grown > point:
            compactions += 1
            summarizer += fill
            fill, m = float(kept), 0
            writes += fill
        else:
            reads += fill
            writes += max(0.0, grown)
            fill, m = fill + grown, m + 1
        total += fill
    requests = len(steps) + 1
    return {"compactions": compactions, "requests": requests, "mean_fill": round(total / requests, 1),
            "context_tokens": round(total, 1), "cache_read_tokens": round(reads, 1),
            "cache_write_tokens": round(writes, 1), "summarizer_read_tokens": round(summarizer, 1)}


def calibrate(steps: list[float], positions: list[int], kept: float, point: float, means: list,
              target: int) -> tuple[float, int, int]:
    """v2: the scale nearest 1 at which the position-aware count at `point` equals `target` (bisection); returns
    (the scale, the count at scale 1, the count at the scale)."""
    def count(scale: float) -> int:
        return simulate_positions(steps, positions, kept, point, means, scale)["compactions"]

    first = count(1.0)
    if first == target:
        return 1.0, first, first
    lo = hi = 1.0
    if first > target:  # too many: shrink the growth; keep count(lo) <= target < count(hi)
        while count(lo) > target and lo > 1e-6:
            lo /= 2
        for _ in range(CALIBRATION_STEPS):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if count(mid) <= target else (lo, mid)
        scale = lo
    else:  # too few: grow it; keep count(lo) < target <= count(hi)
        while count(hi) < target and hi < 1e6:
            hi *= 2
        for _ in range(CALIBRATION_STEPS):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if count(mid) >= target else (mid, hi)
        scale = hi
    return scale, first, count(scale)


def actual_usage(included: list) -> dict:
    """v2: what the included segments' requests' usage records say (the first usage record of each request)."""
    requests = [r for s in included for r in s.requests]
    return {"requests": len(requests), "cache_read_tokens": sum(r.read for r in requests),
            "cache_write_tokens": sum(r.write for r in requests),
            "mean_context": round(statistics.fmean(r.context for r in requests), 1) if requests else None}


def _position_block(steps: list, positions: list, kept: float, observed: int, included: list, rc: dict,
                    rows: list) -> dict:
    """v2: the flat rows' corrected loss, the position-aware variant and the actual usage."""
    losses = _loss_means_v2(rc)
    for row in rows:
        row["loss_v2"] = _scaled(losses, row["compactions"])
    means = growth_means(steps, positions)
    block = {"loss_means_v2": losses, "actual_usage": actual_usage(included),
             "growth_means": {name: (None if m is None else round(m, 1)) for name, m in zip(BUCKET_NAMES, means)},
             "growth_steps": {name: sum(1 for p in positions if p >= 0 and _bucket(p) == b)
                              for b, name in enumerate(BUCKET_NAMES)}}
    if not all(m is not None and math.isfinite(m) and m > 0 for m in means):
        block["position_aware"] = {"rows": [], "why_not": "a bucket's mean growth is missing, not finite or not positive"}
        return block
    scale, unscaled, scaled = calibrate(steps, positions, kept, COST_POINTS[-1], means, observed)
    model_rows = []
    for point in COST_POINTS:
        row = {"X": point, **simulate_positions(steps, positions, kept, point, means, scale),
               "compactions_unscaled": simulate_positions(steps, positions, kept, point, means)["compactions"]}
        row["cache_read_units"] = round(READ_RATIO * row["cache_read_tokens"], 1)
        row["cache_write_units"] = round(WRITE_RATIO * row["cache_write_tokens"], 1)
        row["loss_v2"] = _scaled(losses, row["compactions"])
        model_rows.append(row)
    block["position_aware"] = {"scale": round(scale, 9), "target_compactions": observed,
                               "compactions_at_the_last_x_unscaled": unscaled,
                               "compactions_at_the_last_x": scaled, "rows": model_rows}
    return block


def cost_model(tl: replay.Timeline, rc: dict, shape_set: str | None = None) -> dict:
    v2 = (shape_set or rc.get("shape_set", "v1")) == "v2"
    included = [s for s in tl.segments if _segment_class(tl, s) == "1M_window"]
    excluded = [s.index for s in tl.segments if _segment_class(tl, s) != "1M_window"]
    steps: list[float] = []
    positions: list[int] = []  # v2: each step's position (the request it leaves; -1: the step across a compaction)
    for i, segment in enumerate(included):
        if i:
            steps.append(0.0)  # the step across an observed compaction
            positions.append(-1)
        contexts = [r.context for r in segment.requests]
        steps.extend(float(b - a) for a, b in zip(contexts, contexts[1:]))
        positions.extend(range(len(contexts) - 1))
    starts = [s.requests[0].context for s in included if s.index >= 1]
    if not included or not starts:
        return {"included_segments": len(included), "rows": [],
                "assumptions": list(MODEL_ASSUMPTIONS) + (list(POSITION_ASSUMPTIONS) if v2 else [])}
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
    out = {"model": "MODEL, not a measurement", "included_segments": len(included), "excluded_segments": excluded,
           "kept_start_mean": round(kept, 1), "kept_start_from_segments": len(starts),
           "observed_compactions_in_included": observed, "steps": len(steps),
           "negative_steps": sum(1 for s in steps if s < 0), "loss_means_per_boundary": losses, "rows": rows,
           "read_ratio": READ_RATIO, "write_ratio": WRITE_RATIO, "assumptions": list(MODEL_ASSUMPTIONS)}
    if v2:
        out["assumptions"] += list(POSITION_ASSUMPTIONS)
        out.update(_position_block(steps, positions, kept, observed, included, rc, rows))
    return out


# ---------------------------------------------------------------- the run and the summary

def run(path: str, pin: int, label: str, sidechain: bool, shape_set: str = "v1") -> dict:
    size = os.path.getsize(path)
    if pin > size:
        raise PinBeyondFileSize(f"--pin {pin:,} is beyond the size of {Path(path).name} ({size:,} bytes)")
    tl, tails = timeline(path, pin, sidechain, shape_set)
    rc = compaction_loss(tl, shape_set, tails)
    rb = quality(path, pin, sidechain)
    models = collections.Counter(q.model for q in tl.requests)
    params = {"windows": [_label(n) for n in WINDOWS], "pseudo_gap": PSEUDO_GAP, "fill_bin": FILL_BIN,
              "class_split": CLASS_SPLIT, "cost_points": list(COST_POINTS), "shapes": list(SHAPES),
              "search_markers": {k: [list(g) for g in v] for k, v in SEARCH_MARKERS.items()},
              "gates": [{"gate": g, "marker": m, "rule": r} for g, m, r in GATES],
              "user_cpt": replay.USER_CPT, "stub_tokens": replay.STUB_TOKENS}
    if shape_set == "v2":
        params.update({"shape_set": "v2", "windows": [w[0] for w in WINDOWS_V2], "strict_labels": list(STRICT_LABELS),
                       "loose_labels": list(LOOSE_LABELS), "directions": list(DIRECTIONS),
                       "view_programs": sorted(VIEW_PROGRAMS), "grep_programs": sorted(GREP_PROGRAMS),
                       "read_programs": sorted(READ_PROGRAMS), "git_read": sorted(GIT_READ),
                       "c5_start": C5_START, "c5_step": C5_STEP, "bootstrap": BOOTSTRAP,
                       "position_buckets": list(BUCKET_NAMES),
                       "tail_items": sum(len(v) for v in (tails or {}).values())})
    return {"schema": 1 if shape_set == "v1" else 2, "label": label, "transcript": Path(path).name, "pin": pin,
            "sidechain": sidechain, "params": params,
            "timeline": {"requests": len(tl.requests), "segments_with_requests": len(tl.segments),
                         "boundaries_on_the_thread": len(tl.boundaries),
                         "requests_by_model": dict(sorted(models.items())),
                         "stats": dict(sorted(tl.stats.items()))},
            "rc": rc, "quality": rb, "cost_model": cost_model(tl, rc, shape_set)}


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
    if any(r["params"].get("shape_set") == "v2" for r in runs):
        return write_summary_v2(out, stamp, runs, pins)
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


# ---------------------------------------------------------------- the v2 summary

WINDOW_LABELS_V2 = tuple(w[0] for w in WINDOWS_V2)
SET_NAMES = {"k1_total": "K1's shapes, writes out", "strict_total": "strict shapes",
             "refetch_total": "K1's + strict (refetch_total)", "loose_total": "loose shapes alone",
             "with_loose_total": "K1's + strict + loose"}


def _seed(name: str) -> int:
    return int(hashlib.sha256(name.encode()).hexdigest()[:16], 16)


def _units(points: list, label: str, key: str, by_segment: bool = False) -> list:
    """(calls, requests) per boundary or point that holds the window with at least one request; C5's points summed per
    (run, segment) when by_segment."""
    units: dict = {}
    for i, (run_label, p) in enumerate(points):
        w = p["windows"].get(label)
        if w is None or not w["requests"]:
            continue
        unit = units.setdefault((run_label, p["segment"]) if by_segment else i, [0, 0])
        unit[0] += w[key]["calls"]
        unit[1] += w["requests"]
    return [tuple(u) for u in units.values()]


def _ratio(units: list) -> float | None:
    requests = sum(u[1] for u in units)
    return 100 * sum(u[0] for u in units) / requests if requests else None


def bootstrap(real: list, control: list, replicates: int, seed: int) -> tuple[float, float] | None:
    """The 95% percentile interval of the excess (real rate - control rate, per 100 requests): real and control
    units, (calls, requests) each, resampled with replacement from random.Random(seed) (random() only, stable across
    Python versions); the 2.5th and 97.5th percentiles by nearest rank."""
    if not real or not control:
        return None
    rng = random.Random(seed)
    diffs = []
    for _ in range(replicates):
        r = [real[int(rng.random() * len(real))] for _ in real]
        c = [control[int(rng.random() * len(control))] for _ in control]
        diffs.append(_ratio(r) - _ratio(c))
    diffs.sort()
    return (diffs[max(0, math.ceil(0.025 * len(diffs)) - 1)], diffs[max(0, math.ceil(0.975 * len(diffs)) - 1)])


def _cell(real: list, control: list, name: str, intervals: bool) -> str:
    rate = _ratio(control)
    if rate is None:
        return "—"
    excess = _ratio(real) - rate if _ratio(real) is not None else None
    if excess is None:
        return f"{rate:.2f}"
    text = f"{rate:.2f}: {excess:+.2f}"
    interval = bootstrap(real, control, BOOTSTRAP, _seed(name)) if intervals else None
    return text + (f" [{interval[0]:+.2f}, {interval[1]:+.2f}]" if interval else "")


def _rate_lines(scope: str, real: list, controls: dict, intervals: bool) -> list[str]:
    lines = ["| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |", "|---|---|---|---|---|---|"]
    for key in TOTALS:
        for label in WINDOW_LABELS_V2:
            units = _units(real, label, key)
            rate = _ratio(units)
            cells = []
            for cname, points in controls.items():
                cunits = _units(points, label, key, by_segment=cname == "C5")
                cells.append(_cell(units, cunits, f"{scope}|{key}|{label}|{cname}", intervals))
            lines.append(f"| {SET_NAMES[key]} | {label} | "
                         f"{'—' if rate is None else f'{rate:.2f}'} ({len(units)}; {sum(u[1] for u in units):,}) | "
                         + " | ".join(cells) + " |")
    return lines


def _per_boundary_lines(real: list, controls: dict) -> list[str]:
    lines = ["| shape set | window | real mean requests per boundary | real calls / tokens per boundary | "
             "excess over C1: calls / tokens per boundary | over C2 | over C5 |", "|---|---|---|---|---|---|---|"]
    for key in ("refetch_total", "with_loose_total"):
        for label in WINDOW_LABELS_V2:
            ws = [p["windows"][label] for _, p in real]
            requests = sum(w["requests"] for w in ws)
            if not ws or not requests:
                continue
            calls, tokens = sum(w[key]["calls"] for w in ws), math.fsum(w[key]["tokens"] for w in ws)
            per = requests / len(ws)
            cells = []
            for points in controls.values():
                cs = [p["windows"][label] for _, p in points if label in p["windows"]]
                creq = sum(w["requests"] for w in cs)
                if not creq:
                    cells.append("—")
                    continue
                ccalls, ctokens = sum(w[key]["calls"] for w in cs), math.fsum(w[key]["tokens"] for w in cs)
                cells.append(f"{(calls / requests - ccalls / creq) * per:+.2f} / "
                             f"{(tokens / requests - ctokens / creq) * per:+,.0f}")
            lines.append(f"| {SET_NAMES[key]} | {label} | {per:.2f} | {calls / len(ws):.2f} / {tokens / len(ws):,.0f} | "
                         + " | ".join(cells) + " |")
    return lines


def _label_rate(points: list, label: str, group: str, name: str) -> str:
    calls = requests = 0
    for _, p in points:
        w = p["windows"].get(label)
        if w is None:
            continue
        requests += w["requests"]
        calls += w[group][name]["calls"]
    return "—" if not requests else f"{100 * calls / requests:.2f}"


def _label_lines(real: list, controls: dict) -> list[str]:
    lines = ["| window | label | set | real | C1 | C2 | C5 |", "|---|---|---|---|---|---|---|"]
    for label in ("20", "20-99", "100"):
        for group, names, set_name in (("refetch", SHAPES, "K1"), ("strict", STRICT_LABELS, "strict"),
                                       ("loose", LOOSE_LABELS, "loose")):
            for name in names:
                cells = [_label_rate(points, label, group, name) for points in (real, *controls.values())]
                lines.append(f"| {label} | {name} | {set_name} | " + " | ".join(cells) + " |")
    return lines


def _direction_lines(real: list, controls: dict) -> list[str]:
    lines = ["| window | shape | direction | real | C1 | C2 | C5 |", "|---|---|---|---|---|---|---|"]
    for label in ("20", "100"):
        for shape in SEARCH_SHAPES:
            for direction in ("counted",) + DIRECTIONS:
                cells = []
                for points in (real, *controls.values()):
                    calls = requests = 0
                    for _, p in points:
                        w = p["windows"].get(label)
                        if w is None:
                            continue
                        requests += w["requests"]
                        d = w["directions"][shape]
                        calls += (d["read"] + d["script"] + d["other"]) if direction == "counted" else d[direction]
                    cells.append("—" if not requests else f"{100 * calls / requests:.2f}")
                lines.append(f"| {label} | {shape} | {direction} | " + " | ".join(cells) + " |")
    return lines


def _miss_lines(real: list, c1: list) -> list[str]:
    lines = ["| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited "
             "before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |",
             "|" + "---|" * 10]
    for label in WINDOW_LABELS_V2:
        ws = [p["windows"][label] for _, p in real]
        cs = [p["windows"][label] for _, p in c1]
        paths = sum(w["missed_paths"] for w in ws)
        named = sum(w["missed_paths_read_before"] + w["missed_paths_edited_before"] for w in ws)
        lines.append("| " + " | ".join([
            label, str(len(ws)), _num(_mean([w["requests"] for w in ws]), 1), _num(_mean([w["missed"] for w in ws]), 1),
            _num(_mean([w["missed_paths"] for w in ws]), 1),
            f"{sum(w['missed_paths_read_before'] for w in ws)} / {sum(w['missed_paths_edited_before'] for w in ws)}",
            _pct(named, paths), _num(_mean([w["reused"] for w in ws]), 1), str(len(cs)),
            _num(_mean([w["reused"] for w in cs]), 1)]) + " |")
    return lines


def _rc_v2_lines(scope: str, real: list, controls: dict, intervals: bool, detail: bool) -> list[str]:
    lines = ["#### Re-fetch calls per 100 requests: the control's rate, then the excess"
             + (" and its 95% bootstrap interval" if intervals else ""), ""]
    lines += _rate_lines(scope, real, controls, intervals) + [""]
    lines += ["#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)", ""]
    lines += _per_boundary_lines(real, controls) + [""]
    if detail:
        lines += ["#### By shape and label, per 100 requests", ""] + _label_lines(real, controls) + [""]
        lines += ["#### The search shapes by direction, per 100 requests (`counted` = read + script + other)", ""]
        lines += _direction_lines(real, controls) + [""]
    lines += ["#### The miss", ""] + _miss_lines(real, controls["C1"]) + [""]
    return lines


def _pins_lines(pins: dict | None) -> list[str]:
    if not pins:
        return ["## Pins: NO pins.json in this directory", ""]
    lines = ["## Pins", "", "| file | role | measured at the start | pin | compact_boundary records |",
             "|---|---|---|---|---|"]
    lines += [f"| {p['file']} | {p['role']} | {_num(p['measured'])} | {p['pin']:,} | {p['boundaries']} |"
              for p in pins["pins"]]
    return lines + ["", f"Subagent files with a boundary now but not in the start measurement: "
                        f"{len(pins['not_pinned_with_a_boundary_now'])}.", ""]


def _pct_of(value, actual) -> str:
    return "—" if value is None or not actual else f"{100 * (value - actual) / actual:+.1f}%"


def _cost_v2_lines(cm: dict) -> list[str]:
    if not cm["rows"]:
        return ["No included segment.", ""]
    pa, actual = cm["position_aware"], cm["actual_usage"]
    g, n = cm["growth_means"], cm["growth_steps"]
    lines = ["- Growth per request by position since the segment start: " + "; ".join(
        f"{name} {_num(g[name])} ({n[name]:,} steps)" for name in BUCKET_NAMES) + ".",
        f"- Actual usage of the {actual['requests']:,} included requests: cache reads "
        f"{_num(actual['cache_read_tokens'])}, cache writes {_num(actual['cache_write_tokens'])}, mean context "
        f"{_num(actual['mean_context'])}."]
    if not pa["rows"]:
        return lines + [f"- Position-aware variant not computed: {pa['why_not']}.", ""]
    lines += [f"- Position-aware calibration: scale {pa['scale']:.6f}; compactions at {COST_POINTS[-1]:,}: "
              f"{pa['compactions_at_the_last_x']} (target {pa['target_compactions']}; unscaled "
              f"{pa['compactions_at_the_last_x_unscaled']}).", "",
              "| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) "
              "| mean fill | cache reads | cache writes |", "|" + "---|" * 9]
    for flat, pos in zip(cm["rows"], pa["rows"]):
        lines.append(f"| {flat['X']:,} | {flat['compactions']} | {_num(flat['mean_fill'])} | "
                     f"{_num(flat['cache_read_tokens'])} | {_num(flat['cache_write_tokens'])} | {pos['compactions']} "
                     f"({pos['compactions_unscaled']}) | "
                     f"{_num(pos['mean_fill'])} | {_num(pos['cache_read_tokens'])} | "
                     f"{_num(pos['cache_write_tokens'])} |")
    flat, pos = cm["rows"][-1], pa["rows"][-1]
    lines += ["", f"At {flat['X']:,} against the actual usage: flat cache reads "
                  f"{_pct_of(flat['cache_read_tokens'], actual['cache_read_tokens'])}, writes "
                  f"{_pct_of(flat['cache_write_tokens'], actual['cache_write_tokens'])}, mean fill "
                  f"{_pct_of(flat['mean_fill'], actual['mean_context'])}; position-aware cache reads "
                  f"{_pct_of(pos['cache_read_tokens'], actual['cache_read_tokens'])}, writes "
                  f"{_pct_of(pos['cache_write_tokens'], actual['cache_write_tokens'])}, mean fill "
                  f"{_pct_of(pos['mean_fill'], actual['mean_context'])}.", "",
              "The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled "
              "compactions times the excess per boundary; calls / tokens.", "",
              "| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |", "|" + "---|" * 8]

    def cell(value) -> str:
        return "—" if value is None else f"{_num(value['calls'])} / {_num(value['tokens'])}"
    for name, rows in (("flat", cm["rows"]), ("position-aware", pa["rows"])):
        for row in rows:
            loss = row["loss_v2"]
            cells = []
            for label in ("20", "100"):
                total = loss[label]["refetch_total"]
                cells += [cell(None if total is None else total[c]) for c in ("C1", "C2", "C5")]
            lines.append(f"| {row['X']:,} | {name} | " + " | ".join(cells) + " |")
    return lines + [""]


def write_summary_v2(out: Path, stamp: str, runs: list, pins: dict | None) -> Path:
    if any(r["params"].get("shape_set") != "v2" for r in runs):
        raise ValueError("the directory mixes v1 and v2 runs")
    lines = ["# K1 round 2 results (task #352, D-106): the corrected re-fetch shapes, three controls, a position-aware "
             "cost model", "",
             f"Written by `scripts/jev_trim/compaction.py summary` at {stamp} from `run --shapes v2` outputs. Counts, "
             "sizes, offsets and names only. No recommendation. The brief is `tasks/briefs/jev-trim/K1-R2-brief.md`; "
             "the method is in the module's docstring. A rate is calls per 100 requests, summed over the boundaries "
             "or points; an excess is the real rate minus the control's; [a, b] is the excess's 95% bootstrap "
             "interval (main only, and the subagents pooled).", ""]
    lines += _pins_lines(pins)
    pooled: dict = {"real": [], "C1": [], "C2": [], "C5": []}
    for run_ in runs:
        rc, rb, cm, t = run_["rc"], run_["quality"], run_["cost_model"], run_["timeline"]
        lines += [f"## Run `{run_['label']}`: {run_['transcript']} pinned at {run_['pin']:,} bytes "
                  f"({'sidechain' if run_['sidechain'] else 'main'} thread)", "",
                  f"- Requests {t['requests']:,}; segments with requests {t['segments_with_requests']}; boundaries on the "
                  f"thread {t['boundaries_on_the_thread']}; skipped boundaries {len(rc['skipped'])}; control points: C1 "
                  f"{len(rc['control'])}, C2 {len(rc['control_c2'])}, C5 {len(rc['control_c5'])}; items after a "
                  f"segment's last request kept for C2 {run_['params']['tail_items']}; models "
                  f"{t['requests_by_model']}.", ""]
        tagged = {"real": [(run_["label"], r) for r in rc["boundaries"]],
                  "C1": [(run_["label"], p) for p in rc["control"]],
                  "C2": [(run_["label"], p) for p in rc["control_c2"]],
                  "C5": [(run_["label"], p) for p in rc["control_c5"]]}
        if run_["sidechain"]:
            for key, value in tagged.items():
                pooled[key] += value
        for cls in ("1M_window", "200k_window"):
            real = [x for x in tagged["real"] if x[1]["class"] == cls]
            controls = {c: [x for x in tagged[c] if x[1]["class"] == cls] for c in ("C1", "C2", "C5")}
            if not real and not any(controls.values()):
                continue
            rows = [r for _, r in real]
            lines += [f"### R-C, class `{cls}`: {len(real)} boundaries; control points C1 {len(controls['C1'])}, C2 "
                      f"{len(controls['C2'])}, C5 {len(controls['C5'])}", "",
                      f"- Removed per boundary (modeled, mean): {_num(_mean([r['pre']['tokens_modeled'] for r in rows]))}"
                      f" tokens; last context before (mean) {_num(_mean([r['pre']['last_context'] for r in rows]))}; kept"
                      f" start per boundary (modeled, mean) {_num(_mean([r['kept']['tokens_modeled'] for r in rows]))}; "
                      f"first context after (mean) {_num(_mean([r['kept']['first_context'] for r in rows]))}; postTokens"
                      f" (mean) {_num(_mean([r['kept']['post_tokens'] for r in rows if r['kept']['post_tokens'] is not None]))}.",
                      ""]
            main = not run_["sidechain"]
            lines += _rc_v2_lines(f"{run_['label']}|{cls}", real, controls, main, main)
        lines += ["### R-B, per 100k of fill", ""] + _quality_rows(rb["bins"]) + ["", "### R-B, per segment third", ""]
        lines += _quality_rows(rb["thirds"], "third") + [""]
        lines += [f"### Cost model (MODEL, not a measurement): included segments {cm['included_segments']}, kept start "
                  f"{_num(cm.get('kept_start_mean'))}, observed compactions among them "
                  f"{cm.get('observed_compactions_in_included')}", ""]
        lines += _cost_v2_lines(cm)
    sides = [r for r in runs if r["sidechain"]]
    if sides:
        lines += [f"## Subagent files pooled: {len(sides)} files, {len(pooled['real'])} boundaries; control points C1 "
                  f"{len(pooled['C1'])}, C2 {len(pooled['C2'])}, C5 {len(pooled['C5'])} (every class)", ""]
        lines += _rc_v2_lines("subagents", pooled["real"], {c: pooled[c] for c in ("C1", "C2", "C5")}, True, True)
        lines += ["### R-B, pooled, per 100k of fill", ""] + _quality_rows(_pool([r["quality"]["bins"] for r in sides]))
        lines += ["", "### R-B, pooled, per segment third", ""]
        lines += _quality_rows(_pool([r["quality"]["thirds"] for r in sides]), "third") + [""]
    if runs and runs[0]["cost_model"].get("assumptions"):
        lines += ["## The cost model's assumptions", ""] + [f"- {a}" for a in runs[0]["cost_model"]["assumptions"]]
        lines.append("")
    if runs:
        p = runs[0]["params"]
        lines += ["## Markers and rules", "", "Hook refusals (R-B), by gate:", ""]
        lines += [f"- `{g['gate']}`: `{g['marker']}` ({'at a line start' if g['rule'] == 'line' else 'in an error result'})"
                  for g in p["gates"]]
        lines += ["", "Searches (R-C re-fetch shapes; v2 counts a search's reads only):", ""]
        lines += [f"- `{shape}`: " + "; ".join(" and ".join(f"`{m}`" for m in group) for group in groups)
                  for shape, groups in p["search_markers"].items()]
        lines += ["", f"- Strict labels: {', '.join(p['strict_labels'])}. Loose labels: {', '.join(p['loose_labels'])}.",
                  f"- Views: {', '.join(p['view_programs'])}. Greps: {', '.join(p['grep_programs'])} and `graft ask`. "
                  f"Reads: {', '.join(p['read_programs'])}; git {', '.join(p['git_read'])}.",
                  f"- C5: every {p['c5_step']} requests from request {p['c5_start']}; bootstrap replicates "
                  f"{p['bootstrap']}.", ""]
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
    r.add_argument("--shapes", choices=SHAPE_SETS, default="v1",
                   help="v1: round 1's shapes, byte-identical outputs (the default); v2: round 2's")
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
    try:
        result = run(args.transcript, args.pin, args.label, args.sidechain, args.shapes)
    except PinBeyondFileSize as err:
        print(f"PinBeyondFileSize: {err}", file=sys.stderr)
        return 2
    target = args.out / f"run-{args.label}.json"
    target.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    rc = result["rc"]
    print(f"wrote {target}: {len(rc['boundaries'])} boundaries, {len(rc['control'])} control points, "
          f"{result['quality']['calls']} calls, {time.monotonic() - began:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
