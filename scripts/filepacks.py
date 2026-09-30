#!/usr/bin/env python3
"""filepacks.py — a context pack for every tracked file (P2) and the hook that shows it when a file is touched (P1).

Task #353 (D-106): K2 of docs/research/findings/jev-trim/D105-DESIGN-v1.md §10.4, items P1 and P2 of §10.3. The brief
is tasks/briefs/jev-trim/K2-FILE-PACKS-brief.md.

P2, `build` (after each commit, from scripts/hooks/post-commit, in the background): HEAD is resolved ONCE and that SHA
is threaded to every read (AF-AP-175). One pass over each source finds the tracked files it names, on a whole-path
boundary (`scripts/stack.py` never matches inside `scripts/stack.py.json` or `x/scripts/stack.py`):
  - the ledger, the decision log, the incident log and nine project skills (SKILLS): per file and source the newest 3
    lines (the highest line numbers), each with its line number, the registry id when the line is a registry row
    (D-NNN, AF-AP-NNN), the ledger line's bold headline (at most 160 characters) and a snippet of at most 240
    characters around the file's first mention in the line;
  - the briefs and reports tasks/briefs/**/*.md: a mention is the brief's path, the newest 3 by the brief's last commit;
  - the last 400 commits, from one `git log --name-only`: the newest 3 that changed the file, with their subjects.
A file that has anything gets <state>/filepacks/<path>.json, written atomically and only when its bytes change; the pack
of a file that has nothing any more is removed. <state>/filepacks/TRACKED.txt lists the tracked files (the hook's
boundary), <state>/filepacks/BLOBS.txt holds each one's blob id at that commit (`<path>TAB<blob>` lines, from the same
`ls-tree`) and <state>/filepacks/BUILD.json records the SHA, its tree, the counts, the milliseconds and a random id,
written last: a build first replaces it with a record that names no tree, so a record with a tree describes every pack
beside it, and no two builds write the same record. A named path can only be matched when all of its characters are
path characters (PATH_RX); the tree's paths use none other (measured).

P1, `hook` (PreToolUse on Read, Edit, Write and Bash, through scripts/hook_context.py): the first time a context window
touches a tracked file, its entry is injected (`entry`): for a code file with a code-map pack (scripts/codemap.py, L2a)
the code part first (the enclosing symbol for an Edit, the symbols in range for a Read with offset and limit, else the
file's own entry, each keeping the code map's STALE mark), then the pack's lines, the sources taken in turn (GROUPS),
all cut at a line boundary within PACK_BUDGET bytes. Every byte shown, the readers' own words aside, is committed text
of HEAD's tree or the build's commit history (P2's commit lines, a brief's last commit and date, the head line's
`@commit`), and after a same-tree ref move that history can hold commits HEAD's history lacks (task #353, K2 RE-SCOPE,
D-117):
  - nothing at all (`tree`) unless the build's tree is HEAD's, resolved once per hook call (`git rev-parse HEAD^{tree}`,
    within HEAD_TIMEOUT; a HEAD that cannot be resolved gives nothing): the packs describe the build's commit, and git
    moves HEAD with no hook (a reset, a checkout). Trees, not commits: scripts/push_clean.sh moves the branch to a
    commit with the same tree and no hook runs, and the packs still describe that tree. The record is read again
    after the parts, and a record that changed in between (a build in flight) gives nothing;
  - the code part only when the code-map pack's blob is the file's blob at the build's commit (BLOBS.txt; else `blob`,
    VERIFY-K2 F1) and its symbols are that blob's own ast (`symbols_from: "ast"`; else `symbols`: a pack of an older
    code map took its symbols from a graph), with its registry rows only when the screen that found them ran from the
    build's committed blobs (codemap.SCREENS; else the rows are left out). The code part names no caller, no test and
    no graph's state: that surface went with the re-scope (it carried VERIFY-K2's class for four rounds).
A touch whose code part is left out gets the pack's lines only, and its record says `code_skip`.

A Bash call touches the files named as arguments of a reader command word (READERS) at a command position, as the
System-1 hook's shell parser finds them: quoted text, heredoc bodies and comments are data; a nested shell's script
(`bash -c '…'`, `sh -c "…"`, `eval '…'`) is code, and the closing quote System-1's code text keeps ends its last word.
grep, egrep and rg name files after their pattern (the first operand, unless -e or -f gives it; a -f file is read).
`cd`, `pushd` and `popd` at a command position move the directory later relative paths resolve against; a `cd` inside
`( … )`, `$( … )`, backticks or a child shell's script stays inside it (an `eval` script's does not). A command under
`ssh` or `pc.sh` runs on another host: its words, quoted ones and heredocs included, name no file here. Each command
word's arguments are read from a word list built once per command line, at most WORDS_MAX of them, and at most
FILES_MAX paths a command line (VERIFY-K2 F3: the parse is linear in the command's length). Not followed: a `cd` in a
pipeline (it runs in a subshell), a heredoc fed to a shell, `case` patterns inside a subshell (their `)` ends it early).

Once per window: `file:<path>` (Read, Write, Bash; an Edit sets it too) and `sym:<path>:<symbol>` (Edit) go into
<state>/filepacks-seen/<window>.json under the System-1 WindowLock. At most CALL_MAX files a call (the first named that
inject) and PACK_WINDOW_MAX a window. `hook --reset` (SessionStart) has the System-1 reset's semantics: a compaction
forgets the compacted window, a resume or a clear every window of its session, and a marker idle 7 days goes. When
BUILD.json is the marker of a build that crashed (no build holds the lock), the reset starts one build (`recover`).

Boundary: only files tracked at the last build (TRACKED.txt, one exact line per path), and only while that build's tree
is HEAD's. A path outside the root or with a `..` component and an untracked file give nothing. A pack that is itself a
symbolic link gives nothing (`link`), and so does a code pack whose directory resolves outside .jev/codemap
(`unreadable`) or a pack whose directory resolves outside <state>/filepacks (`link`); a directory link that stays inside
them, a linked .jev/codemap and a linked <state>/filepacks are followed, since the state is trusted (VERIFY-K2 F6). A
working file that is not a regular file gives no code part. Advisory, never a gate: every path exits 0 and prints
nothing on an error; a decision or an error is one JSON line in <state>/filepacks.jsonl (the System-1 record shape:
keys, bytes, sha, why; never the tool input). Off switch: the file <state>/filepacks-off (a dangling link counts; the
reset still runs). A call that names no tracked file, or that comes before the first build, logs nothing and writes no
marker; one while the build's tree is not HEAD's logs its files as skipped (`tree`) and writes no marker. What a call
does write (VERIFY-K2 F12): a payload that is not JSON logs one line, creating <state> when it is missing; the first
call with <state> present caches the System-1 hook's bytecode under <state>/pycache; the import of scripts/codemap.py
caches its bytecode in scripts/__pycache__, which git ignores; a reset that starts a build writes
<state>/filepacks-recover.log, and the build its packs.

`replay` runs the main loop's recorded tool calls through the hook's planner, window by window (split at the compaction
boundaries), with the seen keys in memory, never the live markers. It reads only compaction boundaries and tool_use
inputs, and prints only counts, bytes and milliseconds. `--wrapper K` also times K recorded calls through the real
wrapper and hook, on a temporary copy of the packs.

The System-1 hook (.claude/hooks/system1-context.py) is imported by path, never copied: its shell parser, window ids,
lock, safe opens and bounded stdin. Its bytecode cache goes under <state>/pycache, never beside it in .claude/hooks. The
code map's readers open files with the same safe opens (VERIFY-K2 F2); this module hands them its own import.

<state> is <repo>/.jev. Test seam, read once at start: AF_FILEPACKS_STATE (the state directory instead of <repo>/.jev).

Usage:
  filepacks.py build
  filepacks.py hook [--reset]
  filepacks.py replay --transcript PATH --bytes N [--wrapper K]
"""
from __future__ import annotations

import bisect
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 1
PACK_BUDGET = 1200                   # bytes per file
CALL_MAX = 2                         # files per call: the first named that inject
PACK_WINDOW_MAX = 64                 # files per context window (the K2 probe: p90 60 files touched per window)
TOOLS = ("Read", "Edit", "Write", "Bash")
READERS = frozenset(("cat", "head", "tail", "sed", "awk", "grep", "egrep", "rg", "less", "more", "nl", "wc", "diff",
                     "cmp"))
LINE_SOURCES = (("ledger", "todo/BUILD-TASKLIST.md"), ("decisions", "docs/08_DECISION_LOG.md"),
                ("incidents", "docs/INCIDENT-LOG.md"))
SKILLS = ("env-tool-quirks", "pc-bridge-lanes", "orchestration", "build-loop", "deep-work", "anti-hollow-green",
          "session-continuity", "code-intel-trio", "ouroboros-stdio")
BRIEFS = "tasks/briefs/"
COMMITS = 400
KEEP = 3                             # mentions kept per file and source, per file of briefs, per file of commits
SNIPPET = 240                        # characters
HEADLINE = 160                       # characters
GROUPS = ("ledger", "incidents", "decisions", "briefs", "skills", "commits")   # the order an entry takes them in
GIT_TIMEOUT = 300
HEAD_TIMEOUT = 2                     # seconds the hook waits for `git rev-parse HEAD^{tree}` (a few ms when it answers)
GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")    # each names a repository git would read
OBJECT_RX = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")      # a git object id (SHA-1 or SHA-256)
STALE_MARK = "STALE: the file changed"     # the code map's own freshness mark, in each of its entries

# A path token: a maximal run of path characters that holds a "." or a "/". The lookbehind starts a match only at the
# start of a run, so the scan is linear.
PATH_RX = re.compile(r"(?<![A-Za-z0-9_.@+/-])[A-Za-z0-9_@+-]*[./][A-Za-z0-9_.@+/-]*")
HEADLINE_RX = re.compile(r"\*\*(.+?)\*\*")
REGISTRY_RX = re.compile(r"\|\s*(D-\d+|AF-AP-\d+)\s*\|")
WS_RX = re.compile(r"\s+")
WORD_RX = re.compile(r"[^\s;&|()`]+")                  # a command word, as the System-1 CMD_POS reads one
SEP_RX = re.compile(r"[;&|()\n`]|\$\(")                # where a simple command's words end, in its shell code
NONSPACE_RX = re.compile(r"\S+")
REDIR_RX = re.compile(r"(?:\d+|&)?(?:>>|>&|>\||<<<|<<-|<<|<&|<>|>|<)")
STRUCT_RX = re.compile(r"[()`'\";&|\n]")           # where a frame opens or ends, or a simple command ends, in shell code
# `ssh` and `pc.sh` as System-1's _word sees them (a word, after its last "/"): the quote readers that run on another host
REMOTE_RX = re.compile(r"(?<![^\s;&|()<`/])(?:ssh|pc\.sh)(?![^\s;&|()<])")
WORDS_MAX = 64                       # argument words read after one command word (F3: a bounded scan per position)
FILES_MAX = 64                       # paths one command line gives, in the order named
# grep's and rg's options that take a value: (short letters, long names); the value is the next word unless attached
GREP_VALUES = ("efmABCdD", frozenset(("regexp", "file", "max-count", "after-context", "before-context", "context",
                                      "devices", "directories", "include", "exclude", "exclude-from", "exclude-dir",
                                      "label", "group-separator", "binary-files")))
GREP = {"grep": GREP_VALUES, "egrep": GREP_VALUES,
        "rg": ("ABCdEefgjMmrtT", frozenset((
            "regexp", "file", "glob", "iglob", "type", "type-not", "type-add", "type-clear", "max-count",
            "after-context", "before-context", "context", "max-columns", "max-depth", "threads", "replace", "encoding",
            "sort", "sortr", "color", "colors", "context-separator", "field-context-separator",
            "field-match-separator", "path-separator", "pre", "pre-glob", "max-filesize", "dfa-size-limit",
            "regex-size-limit", "engine", "ignore-file", "hostname-bin", "hyperlink-format")))}

_S1 = None
_CM = None


# ---------------------------------------------------------------- the two modules this one reads through

def s1(cache=None):
    """The System-1 hook, imported by path once per process (its file name has a hyphen). With `cache` its bytecode
    is cached under that directory; without it none is written. Never beside the hook in .claude/hooks."""
    global _S1
    if _S1 is None:
        spec = importlib.util.spec_from_file_location("filepacks_system1",
                                                      ROOT / ".claude" / "hooks" / "system1-context.py")
        mod = importlib.util.module_from_spec(spec)
        saved = sys.pycache_prefix, sys.dont_write_bytecode
        if cache:
            sys.pycache_prefix = str(cache)
        else:
            sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.pycache_prefix, sys.dont_write_bytecode = saved
        _S1 = mod
    return _S1


def codemap():
    """scripts/codemap.py (L2a), imported once per process: its pack paths and its readers. Its readers' safe opens
    come from this process's System-1 module, never from a second import."""
    global _CM
    if _CM is None:
        spec = importlib.util.spec_from_file_location("filepacks_codemap", ROOT / "scripts" / "codemap.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod._S1 = s1()
        _CM = mod
    return _CM


# ---------------------------------------------------------------- paths

def repo_rel(path, cwd, root=ROOT):
    """`path` (absolute, `~/`, or relative to `cwd`) as a repo-relative path, or None: not a non-empty string, a `..`
    component, a relative path with no absolute cwd, or outside the root."""
    if not isinstance(path, str) or not path or "\0" in path or "\n" in path or ".." in path.split("/"):
        return None
    if path.startswith("~/"):
        path = os.path.expanduser(path)
    if not path.startswith("/"):
        if not (isinstance(cwd, str) and cwd.startswith("/")):
            return None
        path = cwd + "/" + path
    norm, base = os.path.normpath(path), os.path.normpath(str(root))
    return norm[len(base) + 1:] if norm.startswith(base + "/") else None


def _inside(path, base):
    """The directory of `path` resolves inside `base`: no symbolic link on the way leads out of it."""
    d, b = os.path.realpath(os.path.dirname(path)), os.path.realpath(base)
    return d == b or d.startswith(b + os.sep)


def _dequote(text):
    """One shell word with its quotes removed; None when it is not one word (an unmatched quote, an empty string)."""
    if not any(c in text for c in "'\"\\"):
        return text
    import shlex
    try:
        parts = shlex.split(text)
    except ValueError:
        return None
    return parts[0] if len(parts) == 1 else None


class _Words:
    """The words of one command line's shell code, split once (F3: the old scan re-read the rest of a simple command
    from every command position in it): a word ends at whitespace, at a separator and at a nested script's closing
    quote, which System-1's code text keeps (`bash -c ;cat a b'`: the last word is `b`, F5). Each word's text is read
    from the command line at the same offsets and dequoted once."""

    def __init__(self, code, cmd, closers):
        bounds = sorted([(m.start(), m.end()) for m in SEP_RX.finditer(code)] + [(k, k + 1) for k in closers])
        self.ends = [a for a, _ in bounds] + [len(code)]
        self.toks, pos = [], 0
        for a, b in bounds + [(len(code), len(code))]:
            self.toks += [(t.start(), t.end()) for t in NONSPACE_RX.finditer(code, pos, a)]
            pos = b
        self.starts = [s for s, _ in self.toks]
        self.code, self.cmd, self.memo = code, cmd, {}

    def after(self, start):
        """The argument words after offset `start` to the end of its simple command, at most WORDS_MAX read; a
        redirection operator and its target are not arguments; None for a word that does not dequote to one."""
        end = self.ends[bisect.bisect_left(self.ends, start)]
        i = bisect.bisect_left(self.starts, start)
        out, skip = [], False
        for s, e in self.toks[i:i + WORDS_MAX]:
            if s >= end:
                break
            if skip:
                skip = False
                continue
            r = REDIR_RX.match(self.code, s, e)
            if r:
                skip = r.end() == e                          # the operator alone: its target is the next word
                continue
            if s not in self.memo:
                self.memo[s] = _dequote(self.cmd[s:e])
            out.append(self.memo[s])
        return out


def _cd(words, cwd):
    """Where a `cd` with these arguments moves to; None when that is unknown (`cd -`, a variable, a word that does not
    dequote)."""
    if words[:1] == ["-"]:
        return None
    args = [w for w in words if w is None or not w.startswith("-")]
    if args[:1] == [None]:
        return None
    d = os.path.expanduser(args[0] if args else "~")
    if "$" in d or "`" in d:
        return None
    if not d.startswith("/"):
        if not (isinstance(cwd, str) and cwd.startswith("/")):
            return None
        d = cwd + "/" + d
    return os.path.normpath(d)


def _shell(cmd, sys1):
    """(code, remote): the command line's shell code, with every `ssh` and `pc.sh` word the System-1 parser reads as a
    quote reader read as a plain word instead, so the quoted words and heredocs it hands to another host are data; and
    the offsets of those words."""
    code = sys1.shell_code(cmd)
    if "ssh" not in cmd and "pc.sh" not in cmd:
        return code, frozenset()
    spans = [m.span() for m in REMOTE_RX.finditer(code)]
    if not spans:
        return code, frozenset()
    chars = list(cmd)
    for a, b in spans:
        chars[a:b] = "_" * (b - a)
    return sys1.shell_code("".join(chars)), frozenset(a for a, _ in spans)


def _frames(code, cmd):
    """(events, closers) of one command line's shell code, in one pass: (offset, "open", kind) where a subshell or a
    `$(` ("sub"), a backtick ("bt") or a nested shell's script ("script", its opening quote, which System-1 writes as
    ";") starts; (offset, "close") where it ends; (offset, "sep") at a separator; and the offsets of the scripts'
    closing quotes, which System-1 keeps. Quoted data is skipped (its text is masked), a substitution inside double
    quotes is not. A single-quoted script ends at the next quote, as System-1 reads it; a `)` with no `(` is ignored."""
    events, closers, stack, squote, i, n = [], [], [], 0, 0, len(code)
    while i < n:
        m = STRUCT_RX.search(code, i)
        if m is None:
            break
        j, c = m.start(), m.group(0)
        i = j + 1
        top = stack[-1] if stack else None
        if c == "'" and squote:                          # a single-quoted script's end: whatever it left open ends too
            while True:
                f = stack.pop()
                if f != "dq":
                    events.append((j, "close"))
                if f == "'":
                    break
            squote -= 1
            closers.append(j)
        elif top == "dq":                                # a double-quoted string: its end and its substitutions only
            if c == '"':
                stack.pop()
            elif c in "(`":
                stack.append("sub" if c == "(" else "bt")
                events.append((j, "open", stack[-1]))
        elif c == ";" and cmd[j] in "'\"":               # a nested shell's script opens
            stack.append(cmd[j])
            squote += cmd[j] == "'"
            events.append((j, "open", "script"))
        elif c == '"' and top == '"':                    # a double-quoted script closes
            stack.pop()
            closers.append(j)
            events.append((j, "close"))
        elif c == "'":                                   # single-quoted data: its text is masked, the next ' ends it
            k = code.find("'", i)
            i = n if k < 0 else k + 1
        elif c == '"':
            stack.append("dq")
        elif c == "(":
            stack.append("sub")
            events.append((j, "open", "sub"))
        elif c == ")":
            if top == "sub":
                stack.pop()
                events.append((j, "close"))
        elif c == "`":
            if top == "bt":
                stack.pop()
                events.append((j, "close"))
            else:
                stack.append("bt")
                events.append((j, "open", "bt"))
        else:
            events.append((j, "sep"))
    return events, closers


def _grep_files(tool, words):
    """The files a grep, egrep or rg command names: its operands after the pattern (the first operand, unless -e or
    -f gives the pattern), and a -f pattern file, which it reads; never an option's value."""
    short, long_ = GREP[tool]
    files, operands, given, i = [], [], False, 0
    while i < len(words):
        w = words[i]
        i += 1
        if w is None or w == "-" or not w.startswith("-"):
            operands.append(w)
        elif w == "--":
            operands += words[i:]
            break
        elif w.startswith("--"):
            name, eq, val = w[2:].partition("=")
            given = given or name in ("regexp", "file")
            if name in long_ and not eq:
                val = words[i] if i < len(words) else None
                i += 1
            if name == "file":
                files.append(val)
        else:
            for k, ch in enumerate(w[1:], 2):
                if ch in short:
                    given = given or ch in "ef"
                    val = w[k:]
                    if not val:
                        val = words[i] if i < len(words) else None
                        i += 1
                    if ch == "f":
                        files.append(val)
                    break
    return files + operands[0 if given else 1:]


def bash_paths(cmd, cwd, root=ROOT):
    """The repo-relative paths a shell command line reads, in order: the arguments of each reader command word at a
    command position of its shell code (the System-1 parser: quoted text, heredoc bodies and comments are data, so
    `echo "cat x"` and `git add x` name nothing), a grep's files after its pattern. `cd`, `pushd` and `popd` move the
    directory the later relative arguments resolve against; a subshell, a substitution or a child shell's script
    restores it when it ends (an `eval` script shares it). A command under `ssh` or `pc.sh` names nothing."""
    sys1 = s1()
    code, remote_at = _shell(cmd, sys1)
    events, closers = _frames(code, cmd)
    words = _Words(code, cmd, closers)
    stack = [[True, None, None, None]]           # frames: [restores, cwd and dirs to restore, its command's word]
    dirs = None                                  # the pushd stack, as (directory, rest) pairs
    out, seen, rels, remote, k = [], set(), {}, 0, 0
    for p in sys1.command_positions(code) + [len(code) + 1]:
        while k < len(events) and events[k][0] < p:
            ev = events[k]
            k += 1
            if ev[1] == "sep":
                stack[-1][3] = None
                if remote == len(stack):
                    remote = 0                   # the command run on another host ends here
            elif ev[1] == "open":
                stack.append([ev[2] != "script" or stack[-1][3] != "eval", cwd, dirs, None])
            else:
                f = stack.pop()
                if f[0]:
                    cwd, dirs = f[1], f[2]
                if remote > len(stack):
                    remote = 0
        if remote or p > len(code):
            continue
        m = WORD_RX.match(code, p)
        word = m.group(0) if m else ""
        stack[-1][3] = word
        if p in remote_at:
            remote = len(stack)                  # this simple command, frames inside it included, runs elsewhere
            continue
        if word not in READERS and word not in ("cd", "pushd", "popd"):
            continue
        args = words.after(m.end())
        if word == "cd":
            cwd = _cd(args, cwd)
        elif word == "pushd":
            dirs = (cwd, dirs)
            cwd = _cd(args, cwd) if len(args) == 1 and args[0] and args[0][0] not in "+-" else None
        elif word == "popd":
            if args:
                cwd = None                       # `popd +N`, `popd -n`: not followed
            elif dirs:
                cwd, dirs = dirs
        else:
            for w in (_grep_files(word, args) if word in GREP else args):
                if w is None or w.startswith("-"):
                    continue
                if (w, cwd) not in rels:                 # one resolution per word and directory (F3)
                    rels[w, cwd] = repo_rel(w, cwd, root)
                r = rels[w, cwd]
                if r and r not in seen:
                    seen.add(r)
                    out.append(r)
                    if len(out) >= FILES_MAX:
                        return out
    return out


def targets(tool, ti, cwd, root=ROOT):
    """The repo-relative paths one tool call touches, in the order named: a Read, Edit or Write's file_path, a Bash
    command's reader arguments."""
    if not isinstance(ti, dict):
        return []
    if tool in ("Read", "Edit", "Write"):
        r = repo_rel(ti.get("file_path"), cwd, root)
        return [r] if r else []
    cmd = ti.get("command") if tool == "Bash" else None
    return bash_paths(cmd, cwd, root) if isinstance(cmd, str) and cmd.strip() else []


# ---------------------------------------------------------------- the reader

class Packs:
    """The packs one hook call or one replay reads: the tracked list, the blob ids, the build's record and whether its
    tree is HEAD's, each read once."""

    def __init__(self, root=ROOT, state=None):
        self.root = Path(root)
        self.state = Path(state) if state else self.root / ".jev"
        self.dir = self.state / "filepacks"
        self._tracked = None
        self._blobs = None
        self._record = None
        self._raw = None
        self._current = None

    def built(self):
        """True once a build wrote TRACKED.txt (a link or another kind of file raises)."""
        if self._tracked is None:
            try:
                self._tracked = s1().read_regular(str(self.dir / "TRACKED.txt"))
            except FileNotFoundError:
                self._tracked = b""
        return bool(self._tracked)

    def tracked(self, rel):
        return self.built() and ("\n%s\n" % rel).encode("utf-8") in self._tracked

    def blob(self, rel):
        """The file's blob id at the build's commit (BLOBS.txt, an exact `\\n<path>\\t` match), or None: not a blob
        there, or no BLOBS.txt yet (a build before it existed). A link or another kind of file raises."""
        if self._blobs is None:
            try:
                self._blobs = s1().read_regular(str(self.dir / "BLOBS.txt"))
            except FileNotFoundError:
                self._blobs = b""
        key = ("\n%s\t" % rel).encode("utf-8")
        i = self._blobs.find(key)
        j = self._blobs.find(b"\n", i + len(key)) if i >= 0 else -1
        return self._blobs[i + len(key):j].decode("ascii", "replace") if j >= 0 else None

    def record(self):
        """BUILD.json: the build's commit, its tree and its counts; {} when it is missing or unreadable (a build in
        flight has replaced it with a record that names no tree). Its bytes are kept for `still`."""
        if self._record is None:
            try:
                self._raw = s1().read_regular(str(self.dir / "BUILD.json"))
                rec = json.loads(self._raw)
            except (OSError, ValueError):
                rec = None
            self._record = rec if isinstance(rec, dict) else {}
        return self._record

    def still(self):
        """True when BUILD.json still holds the bytes `record` read. A build replaces it before it changes any pack
        and ends with a record no other build writes (its id), so the same bytes mean that no build ran while the
        parts were read (D-117 (b))."""
        self.record()
        try:
            return self._raw is not None and s1().read_regular(str(self.dir / "BUILD.json")) == self._raw
        except OSError:
            return False

    def commit(self):
        c = self.record().get("commit")
        return c[:7] if isinstance(c, str) else "?"

    def current(self):
        """True when the build's tree is HEAD's (K2 RE-SCOPE, D-117 condition (b)): BUILD.json's `tree` equals
        `HEAD^{tree}`, resolved once per Packs (one hook call). False when the build recorded no tree (a build from
        before this check) or HEAD cannot be resolved (no repository, an unborn branch, a git error or timeout)."""
        if self._current is None:
            want, got = self.record().get("tree"), _rev(self.root, "HEAD^{tree}")
            self._current = isinstance(want, str) and OBJECT_RX.fullmatch(want) is not None and got == want
        return self._current

    def shown(self, path):
        """A pack's path as the entry names it: repo-relative when it is inside the root."""
        p = str(path)
        return p[len(str(self.root)) + 1:] if p.startswith(str(self.root) + os.sep) else p


def _own_env():
    """os.environ without GIT_ENV: git then finds the repository from the directory it runs in, never from a variable
    its caller left set (VERIFY-K2-RS F4: an inherited GIT_DIR named a clone's HEAD, whose tree was the build's)."""
    return {k: v for k, v in os.environ.items() if k not in GIT_ENV}


def _rev(root, name):
    """`git rev-parse --verify -q NAME` in the repository at `root`, with GIT_ENV removed from its environment
    (_own_env): the object id, or None when git cannot resolve it (no repository, an unborn branch, an error) or does
    not answer within HEAD_TIMEOUT seconds."""
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "--verify", "-q", name], cwd=root, env=_own_env(), capture_output=True,
                           stdin=subprocess.DEVNULL, timeout=HEAD_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    out = r.stdout.decode("ascii", "replace").strip()
    return out if r.returncode == 0 and OBJECT_RX.fullmatch(out) else None


class PackError(Exception):
    """A pack that exists and cannot be used: `why` is link, unreadable or corrupt."""

    def __init__(self, why):
        super().__init__(why)
        self.why = why


def _group(source):
    return "skills" if source.startswith("skill:") else {"brief": "briefs", "commit": "commits"}.get(source, source)


def render(m):
    """One pack mention as one entry line."""
    src = m["source"]
    if src == "commit":
        return "commit %s %s: %s" % (m["commit"], m["date"], m["subject"])
    if src == "brief":
        return "brief %s L%d (%s %s)" % (m["path"], m["line"], m["date"], m["commit"])
    head = "%s L%d" % (src.replace("skill:", "skill "), m["line"])
    if m.get("id"):
        head += " " + m["id"]
    if m.get("headline") and m.get("at"):             # the snippet does not start at the line's headline
        head += " **%s**" % m["headline"]
    return "%s: %s" % (head, m["snippet"])


def _p2_lines(rel, packs):
    """The pack's lines: a head line (the counts and the pack's path), then the mentions, the newest of each source
    group first, the groups taken in turn (GROUPS). [] when the file has no pack; PackError when it cannot be used."""
    path = packs.dir / (rel + ".json")
    if not os.path.lexists(path):
        return []
    if os.path.islink(path) or not _inside(path, packs.dir):
        raise PackError("link")
    try:
        pack = json.loads(s1().read_regular(str(path)).decode("utf-8"))
    except OSError:
        raise PackError("unreadable") from None
    except ValueError:
        raise PackError("corrupt") from None
    try:
        if not isinstance(pack, dict) or pack.get("schema") != SCHEMA or pack.get("path") != rel:
            raise ValueError("another schema or path")
        counts = pack["counts"]
        by = {g: [] for g in GROUPS}
        for m in pack["mentions"]:
            by[_group(m["source"])].append(render(m))
        head = "filepack %s @%s: %s (pack %s)" % (rel, packs.commit(), " · ".join(
            "%s %d" % (g, counts[g]) for g in GROUPS if counts.get(g)), packs.shown(path))
    except (ValueError, KeyError, TypeError, AttributeError):
        raise PackError("corrupt") from None
    out = [head]
    for rank in range(max(len(v) for v in by.values())):
        out += [by[g][rank] for g in GROUPS if rank < len(by[g])]
    return out


def _screened(pack, packs):
    """True when the code-map pack's registry rows came from the build's committed screen: the code map records the blob
    id of each file of the screen it ran (codemap.SCREENS, the screen's code and its table, whose row ids and messages
    the rows carry), and each must be that file's blob at the build (BLOBS.txt)."""
    ins = pack.get("instruments")
    sec = ins.get("ap_screen") if isinstance(ins, dict) else None
    screens = sec.get("screens") if isinstance(sec, dict) else None
    return isinstance(screens, dict) and all(isinstance(screens.get(p), str) and screens[p] == packs.blob(p)
                                             for p in codemap().SCREENS)


def _code_part(rel, ti, packs):
    """(status, text, symbol, stale, skip) of the code map's entry for this touch; status None when there is none, and
    skip "blob" when the code-map pack does not describe the file's blob at the build's commit (VERIFY-K2 F1: then its
    text is not the build's), "symbols" when its symbols are not that blob's own ast (a pack of an older code map took
    them from a graph, D-117 (a)). Its registry rows are left out unless the screen that found them ran from the build's
    committed blobs (_screened). The pack is read once, here, and handed to the reader, so the pack checked is the pack
    shown. An Edit placed in one symbol gives that symbol's entry (a module-level one `<module>`); an Edit that cannot
    be placed gives the file's entry. A Read with offset and limit gives the enclosing symbol's entry, or the symbols in
    range when no one symbol holds the range. PackError when the pack exists and cannot be used."""
    cm = codemap()
    root = packs.root
    path = cm.pack_path(root, rel)
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return None, "", None, None, None
    if not stat.S_ISREG(st.st_mode) or not _inside(path, Path(root) / cm.PACK_DIR):
        raise PackError("link" if stat.S_ISLNK(st.st_mode) else "unreadable")
    try:
        wst = os.lstat(Path(root) / rel)
        if not stat.S_ISREG(wst.st_mode):
            return None, "", None, None, None            # a link, a FIFO: the code map never reads it
    except FileNotFoundError:
        pass                                             # gone from the working tree: the code map says STALE
    try:
        pack = json.loads(s1().read_regular(str(path)).decode("utf-8"))
    except FileNotFoundError:
        raise PackError("gone") from None
    except OSError:
        raise PackError("unreadable") from None
    except ValueError:
        raise PackError("corrupt") from None
    if not isinstance(pack, dict) or pack.get("schema") != cm.SCHEMA or not isinstance(pack.get("blob"), str):
        raise PackError("corrupt")
    if pack["blob"] != packs.blob(rel):
        return None, "", None, None, "blob"
    if pack.get("symbols_from") != "ast":
        return None, "", None, None, "symbols"          # D-117 (a): only the committed blob's own ast names symbols
    if not _screened(pack, packs):
        pack["registry"] = []                           # a row id or message the build's screen does not hold

    def use(r):
        if r["status"] in ("out-of-scope", "miss"):
            return None, "", None, None, None
        return r["status"], r["text"], None, r.get("stale"), None

    old = ti.get("old_string")
    if isinstance(old, str) and old:
        r = cm.edit_context(str(Path(root) / rel), old, root=root, replace_all=ti.get("replace_all") is True,
                            pack=pack)
        if r["status"] in ("hit", "module"):
            sym = r["symbol"]["qualname"] if r["status"] == "hit" else "<module>"
            return r["status"], r["text"], sym, r["stale"], None
        return use(cm.file_entry(rel, root=root, pack=pack))     # not placed: the file's own entry
    off, lim = ti.get("offset"), ti.get("limit")
    if type(off) is int and type(lim) is int and off >= 0 and lim >= 1:
        lo = max(off, 1)
        r = cm.lookup(rel, lo, lo + lim - 1, root=root, pack=pack)
        if r["status"] == "module":                    # no one symbol holds the range: the symbols in it
            r = cm.file_entry(rel, lo, lo + lim - 1, root=root, pack=pack)
        return use(r)
    return use(cm.file_entry(rel, root=root, pack=pack))


def entry(rel, tool_input, budget=PACK_BUDGET, *, packs=None, p2=True):
    """What the hook injects for one touch of the tracked file `rel`: nothing unless the build's tree is HEAD's and its
    record is unchanged once the parts are read (skip "tree", D-117 (b)); else the code part (see _code_part), then the
    pack's lines (unless `p2` is false), cut at a line boundary within `budget` bytes. A stale code part is never shown
    without its STALE mark: when the mark does not fit, nothing is. Returns {text, symbol (an Edit's), code (the code
    part's status or None), stale, skip (tree: why nothing; blob or symbols: why the code part was left out), lines,
    cut, error (why nothing: link, unreadable, corrupt or gone)}."""
    packs = packs or Packs()
    ti = tool_input if isinstance(tool_input, dict) else {}
    res = {"text": "", "symbol": None, "code": None, "stale": None, "skip": None, "lines": 0, "cut": 0, "error": None}
    if not packs.current():
        return dict(res, skip="tree")                    # D-117 (b): the packs describe a tree that is not HEAD's
    try:
        status, text, sym, stale, skip = _code_part(rel, ti, packs)
        lines = text.split("\n") if text else []
        lines += _p2_lines(rel, packs) if p2 else []
    except PackError as e:
        return dict(res, error=e.why)
    if not packs.still():
        return dict(res, skip="tree")                    # a build began while the parts were read: they may be its
    kept, used = [], 0
    for ln in lines:
        cost = len(ln.encode("utf-8")) + (1 if kept else 0)
        if used + cost > budget:
            break
        kept.append(ln)
        used += cost
    if stale and not any(STALE_MARK in ln for ln in kept):
        kept = []                                        # a stale code part never passes as fresh
    return dict(res, text="\n".join(kept), symbol=sym, code=status, stale=stale, skip=skip, lines=len(kept),
                cut=len(lines) - len(kept))


# ---------------------------------------------------------------- the hook

def touched(payload, packs):
    """The tracked files one PreToolUse payload touches, in the order named; [] before the first build."""
    tool = payload.get("tool_name")
    if tool not in TOOLS or not packs.built():
        return []
    return [r for r in targets(tool, payload.get("tool_input"), payload.get("cwd"), packs.root) if packs.tracked(r)]


def plan(payload, rels, seen, packs, budget=PACK_BUDGET, timings=None):
    """(text, record, new keys) for the tracked files `rels` one PreToolUse payload touches. `seen` (the window's keys)
    is not changed. `timings` collects each entry's milliseconds (the replay's measure)."""
    tool, ti, tuid = payload.get("tool_name"), payload.get("tool_input"), payload.get("tool_use_id")
    rec = {"event": "PreToolUse", "tool": tool, "tool_use_id": tuid if isinstance(tuid, str) else None,
           "injected": [], "skipped": [], "bytes": 0}
    taken = set(seen)
    files = sum(1 for k in taken if k.startswith("file:"))
    blocks, new = [], []
    for rel in rels:
        fkey = "file:" + rel
        if len(blocks) >= CALL_MAX:
            rec["skipped"].append({"key": fkey, "why": "call-max"})
            continue
        if fkey not in taken and files >= PACK_WINDOW_MAX:
            rec["skipped"].append({"key": fkey, "why": "window-max"})
            continue
        if tool != "Edit" and fkey in taken:
            rec["skipped"].append({"key": fkey, "why": "duplicate"})
            continue
        t0 = time.perf_counter()
        e = entry(rel, ti, budget, packs=packs, p2=fkey not in taken)
        if timings is not None:
            timings.append((time.perf_counter() - t0) * 1000)
        key = "sym:%s:%s" % (rel, e["symbol"]) if tool == "Edit" and e["symbol"] else fkey
        if e["error"]:
            rec["skipped"].append({"key": key, "why": e["error"]})
            continue
        if key in taken:
            rec["skipped"].append({"key": key, "why": "duplicate"})
            continue
        if not e["text"]:
            rec["skipped"].append({"key": key, "why": "budget" if e["cut"] else e["skip"] or "no-pack"})
            continue
        keys = [key] + ([fkey] if fkey != key and fkey not in taken else [])
        files += fkey not in taken
        taken.update(keys)
        new += keys
        blocks.append(e["text"])
        inj = {"key": key, "bytes": len(e["text"].encode("utf-8")), "lines": e["lines"],
               "sha": hashlib.sha256(e["text"].encode("utf-8")).hexdigest()[:16], "code": e["code"]}
        if e["cut"]:
            inj["cut"] = e["cut"]
        if e["stale"]:
            inj["stale"] = True
        if e["skip"]:
            inj["code_skip"] = e["skip"]
        rec["injected"].append(inj)
    text = "\n".join(blocks)
    rec["bytes"] = len(text.encode("utf-8")) if text else 0
    return text, rec, new


def reset(payload, state, now):
    """SessionStart, with the System-1 reset's semantics on <state>/filepacks-seen: a compaction forgets the compacted
    window, a resume or a clear every window of the session; a marker idle MARKER_MAX_AGE_S goes whatever the source.
    Then `recover`: a build that crashed after its marker gets one new build."""
    sys1 = s1()
    seen_dir = Path(state) / "filepacks-seen"
    src = payload.get("source")
    wid = sys1.window_id(payload)
    sid = wid.split(".", 1)[0]
    removed = 0
    for name in sorted(os.listdir(seen_dir)) if seen_dir.is_dir() else []:
        path = seen_dir / name
        hit = (src == "compact" and name in (wid + ".json", wid + ".json.lock")) or (
            src in ("resume", "clear") and name.startswith(sid + "."))
        try:
            if hit or now - os.lstat(path).st_mtime > sys1.MARKER_MAX_AGE_S:
                os.unlink(path)
                removed += name.endswith(".json")
        except FileNotFoundError:
            pass
    return dict({"event": "SessionStart", "source": src if isinstance(src, str) else None, "removed": removed},
                **recover(state))


def recover(state):
    """VERIFY-K2-RS F15: a build that crashed after its marker (`"building": true`, no tree) leaves the hook showing
    nothing until a build writes its record, and without this only the next commit's build would. When BUILD.json is
    that marker and no build holds <state>/filepacks.lock, one build of HEAD starts in the background: a new session,
    niced, in this repository (_own_env), its output in <state>/filepacks-recover.log. The session start waits for the
    spawn, never for the build. While a build holds the lock, none starts: the marker is that build's. Returns the
    reset record's part: {} (the record is not a marker), {"rebuild": "busy"} or {"rebuild": "started", "pid": N}."""
    import fcntl
    import subprocess
    sys1 = s1()
    try:
        rec = json.loads(sys1.read_regular(str(Path(state) / "filepacks" / "BUILD.json")))
    except (OSError, ValueError):
        return {}
    if not isinstance(rec, dict) or rec.get("building") is not True:
        return {}
    lock = sys1.open_regular(str(Path(state) / "filepacks.lock"), os.O_WRONLY | os.O_CREAT)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return {"rebuild": "busy"}
    finally:
        os.close(lock)            # free before the build takes it: the build's own lock keeps builds one at a time
    out = sys1.open_regular(str(Path(state) / "filepacks-recover.log"), os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    try:
        p = subprocess.Popen([sys.executable, str(ROOT / "scripts" / "filepacks.py"), "build"], cwd=str(ROOT),
                             env=dict(_own_env(), AF_FILEPACKS_STATE=str(state)), stdin=subprocess.DEVNULL, stdout=out,
                             stderr=out, start_new_session=True, preexec_fn=lambda: os.nice(19))
    finally:
        os.close(out)
    return {"rebuild": "started", "pid": p.pid}


def log(state, rec):
    """One JSON line in <state>/filepacks.jsonl (0600, never through a link, never blocking on a FIFO); it moves to
    .1 past the System-1 log's size. A failed write loses the line, never the hook."""
    try:
        sys1 = s1()
        path = os.path.join(state, "filepacks.jsonl")
        os.makedirs(state, mode=0o700, exist_ok=True)
        try:
            if os.path.getsize(path) > sys1.LOG_MAX_BYTES:
                os.replace(path, path + ".1")
        except FileNotFoundError:
            pass
        fd = sys1.open_regular(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        try:
            os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
        finally:
            os.close(fd)
    except Exception:
        pass                                             # telemetry never breaks the hook


def hook(argv, state):
    """`hook` (PreToolUse) and `hook --reset` (SessionStart). Always exits 0; prints the entries or nothing."""
    started = time.monotonic()
    resetting = argv == ["--reset"]
    if not resetting and os.path.lexists(state / "filepacks-off"):          # a dangling link counts
        return 0
    rec, text, tool, wid = None, "", None, None
    try:
        sys1 = s1(state / "pycache" if state.is_dir() else None)
        payload = json.loads(sys1.read_stdin().decode("utf-8") or "null")
        if not isinstance(payload, dict):
            return 0
        tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else None
        if resetting:
            if not state.is_dir():
                return 0                                 # nothing to forget
            rec = reset(payload, state, time.time())
        elif payload.get("hook_event_name") == "PreToolUse":
            packs = Packs(ROOT, state)
            rels = touched(payload, packs)
            if not rels:
                return 0                                 # no tracked file, or no build yet: no log line, no marker
            wid = sys1.window_id(payload)
            marker = str(state / "filepacks-seen" / (wid + ".json"))
            with sys1.WindowLock(marker):
                seen = sys1.load_seen(marker)
                text, rec, new = plan(payload, rels, seen, packs)
                if new:
                    sys1.write_json_atomic(marker, {"keys": sorted(seen | set(new))})
            rec["window"] = wid
        else:
            return 0
    except BaseException as exc:                         # fail quiet: nothing injected, the type logged
        text = ""
        rec = {"event": "SessionStart" if resetting else "PreToolUse", "tool": tool, "error": type(exc).__name__}
        if wid:
            rec["window"] = wid
    rec["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["ms"] = round((time.monotonic() - started) * 1000, 1)
    log(state, rec)
    if text:
        sys.stdout.write(text + "\n")
    return 0


# ---------------------------------------------------------------- the builder (P2)

def _git(root, *args, data=None):
    import subprocess
    r = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=root, input=data, capture_output=True,
                       timeout=GIT_TIMEOUT)
    if r.returncode != 0:
        raise RuntimeError("git %s exited %d: %s" % (args[0], r.returncode,
                                                     r.stderr.decode("utf-8", "replace").strip()[-200:]))
    return r.stdout


def _blobs(root, sha, paths):
    """{path: text} of each path at `sha`, from one `git cat-file --batch`; None for one that is not a blob there."""
    out = _git(root, "cat-file", "--batch", data="".join("%s:%s\n" % (sha, p) for p in paths).encode("utf-8"))
    res, i = {}, 0
    for p in paths:
        nl = out.index(b"\n", i)
        head = out[i:nl].split()
        if len(head) == 3 and head[1] == b"blob":
            size = int(head[2])
            res[p] = out[nl + 1:nl + 1 + size].decode("utf-8", "replace")
            i = nl + 1 + size + 1
        else:
            res[p] = None
            i = nl + 1 + (int(head[2]) + 1 if len(head) == 3 else 0)
    return res


def _log(root, sha, limit=None, path=None):
    """[(sha, date, subject, [paths])], newest first, from one `git log --name-only` at `sha`: at most `limit`
    commits, only those that changed something under `path`."""
    out = _git(root, "log", "--no-renames", "--format=%x1e%H%x1f%cs%x1f%s", "--name-only",
               *(["-n", str(limit)] if limit else []), sha, *(["--", path] if path else [])).decode("utf-8", "replace")
    res = []
    for chunk in out.split("\x1e")[1:]:
        head, _, names = chunk.partition("\n")
        h, d, s = (head.split("\x1f") + ["", ""])[:3]
        res.append((h, d, s, [n for n in names.split("\n") if n]))
    return res


def _cut(text, width):
    text = WS_RX.sub(" ", text).strip()
    return text if len(text) <= width else text[:width - 1] + "…"


def _snippet(line, pos, n):
    """At most SNIPPET characters of `line` around its characters [pos, pos + n), whitespace folded, each cut end marked
    `…`; and the column it starts at (0: the line's start)."""
    if len(line) <= SNIPPET:
        return WS_RX.sub(" ", line).strip(), 0
    a = max(0, min(pos - (SNIPPET - n) // 2, len(line) - SNIPPET))
    s = line[a:a + SNIPPET]
    if a > 0:
        s = "…" + s[1:]
    if a + SNIPPET < len(line):
        s = s[:-1] + "…"
    return WS_RX.sub(" ", s).strip(), a


def _line_mention(source, n, line, m):
    snip, at = _snippet(line, m.start(), m.end() - m.start())
    rec = {"source": source, "line": n, "snippet": snip, "at": at}
    rid = REGISTRY_RX.match(line)
    if rid:
        rec["id"] = rid.group(1)
    h = HEADLINE_RX.match(line) if source == "ledger" else None
    if h:
        rec["headline"] = _cut(h.group(1), HEADLINE)
    return rec


def _path(tok, tracked, prefix):
    """The tracked file a path token names: as written or without a trailing `.` (a sentence's end), after the repo
    root's absolute prefix or a `./`; None when it names none."""
    for t in (tok, tok.rstrip(".")):
        if t.startswith(prefix):
            t = t[len(prefix):]
        elif t.startswith("./"):
            t = t[2:]
        if t in tracked:
            return t
    return None


def _write(path, raw):
    """`raw` into <path>.<pid>.tmp, renamed over `path` (0600, never through a link); a failed write leaves no temp."""
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    fd = s1().open_regular(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    try:
        try:
            view = memoryview(raw)
            while view:
                view = view[os.write(fd, view):]
        finally:
            os.close(fd)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _clean(pdir, keep):
    """Remove from `pdir` every pack whose file is not in `keep`, every temp file, every symbolic link (never ours) and
    each directory left empty. Returns the number of packs removed."""
    removed = 0
    for dirpath, dirnames, filenames in os.walk(pdir, topdown=False):
        top = os.path.samefile(dirpath, pdir)
        for name in filenames + [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]:
            full = os.path.join(dirpath, name)
            link = os.path.islink(full)
            if top and name in ("BUILD.json", "TRACKED.txt", "BLOBS.txt") and not link:
                continue
            rel = os.path.relpath(full, pdir)
            if link or not name.endswith(".json") or rel[:-5] not in keep:
                try:
                    os.unlink(full)
                    removed += name.endswith(".json") and not link
                except OSError:
                    pass
        if not top:
            try:
                os.rmdir(dirpath)                        # only when empty
            except OSError:
                pass
    return removed


def build(root=ROOT, state=None, sha=None):
    """Build every pack at one commit: `sha`, else HEAD resolved once here (AF-AP-175). One build at a time (a lock in
    <state>). Returns the BUILD.json record (the commit, its tree, the counts)."""
    import fcntl
    t0 = time.monotonic()
    root = Path(root)
    state = Path(state) if state else root / ".jev"
    os.makedirs(state, mode=0o700, exist_ok=True)
    lock = s1(state / "pycache").open_regular(str(state / "filepacks.lock"), os.O_WRONLY | os.O_CREAT)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _build(root, state, sha, t0)
    finally:
        os.close(lock)


def _build(root, state, sha, t0):
    if sha is None:
        sha = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("not a full commit id: %r" % sha[:80])
    tree = _git(root, "rev-parse", "--verify", sha + "^{tree}").decode("ascii").strip()    # the reader's check (D-117)
    tracked, blobs = [], []                              # one ls-tree: the paths and each blob id
    for item in _git(root, "ls-tree", "-r", "-z", sha).decode("utf-8", "replace").split("\0"):
        meta, tab, p = item.partition("\t")                # "<mode> <type> <object>\t<path>"
        if not tab or not p or "\n" in p:
            continue
        tracked.append(p)
        kind, obj = (meta.split(" ") + ["", ""])[1:3]
        if kind == "blob" and "\t" not in p:
            blobs.append("%s\t%s" % (p, obj))
    tset = set(tracked)
    line_sources = list(LINE_SOURCES) + [("skill:" + s, ".claude/skills/%s/SKILL.md" % s) for s in SKILLS]
    briefs = sorted(p for p in tracked if p.startswith(BRIEFS) and p.endswith(".md"))
    missing = [path for _, path in line_sources if path not in tset]
    texts = _blobs(root, sha, [path for _, path in line_sources if path in tset] + briefs)
    counts, kept = {}, {}

    def hit(p, source, make):
        c = counts.setdefault(p, {})
        c[_group(source)] = c.get(_group(source), 0) + 1
        lst = kept.setdefault(p, {}).setdefault(source, [])
        if len(lst) < KEEP:
            lst.append(make())

    prefix = str(root) + "/"
    for source, path in line_sources:                    # the newest (highest) lines first
        lines = (texts.get(path) or "").split("\n")
        for i in range(len(lines) - 1, -1, -1):
            found = {}
            for m in PATH_RX.finditer(lines[i]):
                p = _path(m.group(0), tset, prefix)
                if p and p not in found:
                    found[p] = m
            for p, m in found.items():
                hit(p, source, lambda: _line_mention(source, i + 1, lines[i], m))
    order, dated = [], set()                             # the briefs, newest first by their last commit
    for h, d, _, names in _log(root, sha, path=BRIEFS):
        for n in names:
            if n in texts and n not in dated and n.startswith(BRIEFS):
                dated.add(n)
                order.append((n, h[:7], d))
    order += [(b, "?", "?") for b in briefs if b not in dated]
    for b, bsha, bdate in order:                         # a mention is the brief's path
        text, named, line_no, last = texts.get(b) or "", set(), 1, 0
        for m in PATH_RX.finditer(text):
            p = _path(m.group(0), tset, prefix)
            if not p or p == b or p in named:
                continue
            named.add(p)
            line_no += text.count("\n", last, m.start())
            last = m.start()
            hit(p, "brief", lambda: {"source": "brief", "path": b, "line": line_no, "commit": bsha, "date": bdate})
    for h, d, subj, names in _log(root, sha, limit=COMMITS):
        for p in dict.fromkeys(names):
            if p in tset:
                hit(p, "commit", lambda: {"source": "commit", "commit": h[:7], "date": d, "subject": _cut(subj, SNIPPET)})
    sources = [s for s, _ in line_sources] + ["brief", "commit"]
    packs = {p: {"schema": SCHEMA, "path": p, "counts": counts[p],
                 "mentions": [m for s in sources for m in by.get(s, ())]}
             for p, by in kept.items() if p != "BUILD"}      # a root file named BUILD would be BUILD.json
    pdir = state / "filepacks"
    os.makedirs(pdir, mode=0o700, exist_ok=True)
    _write(str(pdir / "BUILD.json"), (json.dumps({"schema": SCHEMA, "commit": sha, "building": True}, sort_keys=True)
                                      + "\n").encode("utf-8"))      # no tree while the packs change (D-117 (b))
    removed = _clean(pdir, set(packs))
    written = failed = 0
    sys1 = s1()
    for p in sorted(packs):
        raw = (json.dumps(packs[p], sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        path = str(pdir / (p + ".json"))
        try:
            if sys1.read_regular(path) == raw:
                continue
        except OSError:
            pass
        try:
            _write(path, raw)
            written += 1
        except OSError:
            failed += 1                                  # a path the pack tree cannot hold: that file goes without
    _write(str(pdir / "BLOBS.txt"), ("\n" + "\n".join(blobs) + "\n").encode("utf-8"))
    _write(str(pdir / "TRACKED.txt"), ("\n" + "\n".join(tracked) + "\n").encode("utf-8"))
    rec = {"schema": SCHEMA, "commit": sha, "tree": tree, "tracked": len(tracked), "files": len(packs),
           "written": written, "removed": removed, "failed": failed, "missing": missing,
           "ms": round((time.monotonic() - t0) * 1000), "id": os.urandom(8).hex()}   # this build's own (Packs.still)
    _write(str(pdir / "BUILD.json"), (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
    return rec


# ---------------------------------------------------------------- the dry run

def _recorded(transcript, cap):
    """[[(tool, input)] per context window]: the main loop's Read, Edit, Write and Bash tool_use inputs in the first
    `cap` bytes of a transcript, split at its compaction boundaries. Only lines naming a compaction boundary or a
    tool_use are parsed, and only those two parts are read; sidechain (subagent) records are left out."""
    windows, read = [[]], 0
    with open(transcript, "rb") as fh:
        for raw in fh:
            if read >= cap:
                break
            raw = raw[:cap - read]                       # the line the cap cuts no longer parses
            read += len(raw)
            if b'"compact_boundary"' not in raw and b'"tool_use"' not in raw:
                continue
            try:
                rec = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(rec, dict):
                continue
            if rec.get("type") == "system" and rec.get("subtype") == "compact_boundary":
                windows.append([])
                continue
            msg = rec.get("message")
            content = msg.get("content") if isinstance(msg, dict) else None
            if rec.get("type") != "assistant" or rec.get("isSidechain") or not isinstance(content, list):
                continue
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") in TOOLS:
                    windows[-1].append((block["name"], block.get("input")))
    return windows


def _pct(vals, q):
    s = sorted(vals)
    return s[min(len(s) - 1, int(q * len(s)))] if s else 0


def replay(transcript, cap, root=ROOT, state=None, wrapper=0, out=None):
    """The hook's planner over the recorded calls, window by window, the seen keys in memory. Prints per window the
    calls, the injections and their bytes, then the median, p90 and max, and the milliseconds of each entry."""
    import statistics
    out = out or sys.stdout
    packs = Packs(root, state)
    if not packs.built():
        print("filepacks replay: no build in %s (run `filepacks.py build` first)" % packs.dir, file=sys.stderr)
        return 2
    windows = _recorded(transcript, cap)
    per, timings = [], []
    for calls in windows:
        seen, inj, nbytes = set(), 0, 0
        for name, ti in calls:
            payload = {"hook_event_name": "PreToolUse", "tool_name": name, "tool_input": ti, "cwd": str(root)}
            rels = touched(payload, packs)
            if rels:
                text, rec, new = plan(payload, rels, seen, packs, timings=timings)
                seen |= set(new)
                inj += len(rec["injected"])
                nbytes += rec["bytes"]
        per.append((len(calls), inj, nbytes))
    for k, (n, i, b) in enumerate(per):
        print("window %d: calls %d injections %d bytes %d" % (k, n, i, b), file=out)
    for label, vals in (("injections", [i for _, i, _ in per]), ("bytes", [b for _, _, b in per])):
        print("%s per window: median %s p90 %s max %s (windows %d)" % (
            label, statistics.median(vals), _pct(vals, .9), max(vals), len(vals)), file=out)
    print("entry ms: p50 %.3f p95 %.3f max %.3f over %d entries" % (
        _pct(timings, .5), _pct(timings, .95), max(timings or [0]), len(timings)), file=out)
    if wrapper:
        _wrapper_latency(windows, wrapper, root, packs, out)
    return 0


def _wrapper_latency(windows, k, root, packs, out):
    """K recorded calls, spread evenly over the transcript, through the real wrapper and hook (a subprocess each), on a
    temporary copy of the packs: the milliseconds each call takes."""
    import shutil
    import subprocess
    import tempfile
    calls = [(w, name, ti) for w, cs in enumerate(windows) for name, ti in cs]
    step = max(1, len(calls) // k)
    tmp = Path(tempfile.mkdtemp(prefix="filepacks-replay-"))
    try:
        shutil.copytree(packs.dir, tmp / "filepacks", symlinks=True)
        env = dict(os.environ, AF_FILEPACKS_STATE=str(tmp), AF_S1_RATE_STATE=str(tmp))
        cmd = ["python3", str(root / "scripts" / "hook_context.py"), "PreToolUse", "--", "python3",
               str(root / "scripts" / "filepacks.py"), "hook"]
        ms, printed = [], 0
        for w, name, ti in calls[::step][:k]:
            data = json.dumps({"hook_event_name": "PreToolUse", "tool_name": name, "tool_input": ti,
                               "cwd": str(root), "session_id": "replay-%d" % w}).encode("utf-8")
            t0 = time.monotonic()
            r = subprocess.run(cmd, input=data, capture_output=True, env=env, timeout=60)
            ms.append((time.monotonic() - t0) * 1000)
            printed += bool(r.stdout.strip())
            if r.returncode != 0:
                raise RuntimeError("the wrapped hook exited %d" % r.returncode)
        print("wrapper ms: p50 %.1f p95 %.1f max %.1f over %d calls (%d injected)" % (
            _pct(ms, .5), _pct(ms, .95), max(ms or [0]), len(ms), printed), file=out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- the command line

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    state = Path(os.environ.get("AF_FILEPACKS_STATE") or ROOT / ".jev")
    if argv[:1] == ["hook"]:
        return hook(argv[1:], state)
    import argparse
    ap = argparse.ArgumentParser(prog="filepacks.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    rp = sub.add_parser("replay")
    rp.add_argument("--transcript", required=True)
    rp.add_argument("--bytes", type=int, required=True)
    rp.add_argument("--wrapper", type=int, default=0)
    ns = ap.parse_args(argv)
    if ns.cmd == "build":
        rec = build(ROOT, state)
        print("filepacks build: %s %d packs (%d written, %d removed, %d failed) of %d tracked files in %d ms%s" % (
            rec["commit"][:7], rec["files"], rec["written"], rec["removed"], rec["failed"], rec["tracked"], rec["ms"],
            "; not tracked: " + ", ".join(rec["missing"]) if rec["missing"] else ""), flush=True)
        return 0
    return replay(ns.transcript, ns.bytes, ROOT, state, ns.wrapper)


if __name__ == "__main__":
    if sys.argv[1:2] == ["hook"]:
        try:
            sys.exit(main())
        except BaseException:
            sys.exit(0)
    sys.exit(main())
