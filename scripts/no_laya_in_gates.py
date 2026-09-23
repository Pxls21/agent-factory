#!/usr/bin/env python3
"""Advisory-exclusion screen: no Laya/Jev vocabulary in gate-defining files.

KC-J1 mechanism -- an absorbing barrier with no bypass.  Exit codes:
  0   clean
  3   violation (one line per hit: <path>:<line>:<token>)
  4   completeness control (gate-file-unlisted, gate-file-missing, gate-file-not-regular,
      gate-file-unreadable, gate-file-sources, gate-file-unparseable,
      gate-file-import-unlisted, gate-file-import-unresolved or gate-file-import-ambiguous)
  64  usage error

Include edges (AMENDMENT 2, J1-0-R3; AMENDMENT 3, J1-0-R4; AF-AP-120, AF-AP-143): the screen reads
the TEXT of listed files, so it also closes the edges through which a listed file pulls other code
INTO ITS OWN PROCESS.
- Shell: a `source` or `.` command in a non-Python gate file is refused unless its exact
  (file, target) pair is in the closed ALLOWED_SOURCES set (two today, neither loads repo code).
  The scan follows bash's quoting, expansion, arithmetic, case and heredoc rules; a workflow file
  is parsed (PyYAML) and each `run:` value is scanned as its own shell text. A text the scan
  cannot finish in sync (a quote, heredoc, $(, ${, $(( or backtick still open at its end, or a
  heredoc word holding $' and a backslash, whose escape bash translates and the scan does not)
  and a workflow that does not parse are refused (gate-file-unparseable), never skipped.
- Python: every static import resolves to the standard library, the closed EXTERNAL_MODULES set,
  or a LISTED repo file (then screened like any other listed file). Every dynamic load into the
  gate's process (spec_from_file_location, SourceFileLoader, runpy.run_path, import_module,
  __import__, and exec, eval or compile of a file's text, or of inline text that imports or loads)
  resolves statically to a listed file (a module name may also be stdlib or EXTERNAL_MODULES), or
  is one of the closed ALLOWED_DYNAMIC_LOADS within its count, or is refused.
Declared limits, not followed: EXEC edges, where a gate file runs another repo script in a
separate process (`bash harness-ports/bin/x.sh`, `python3 "$AF_REPO/scripts/y.py"`). Many are built
from variables no lexical rule can resolve, and a fail-closed rule would block every commit.
Measured at AMENDMENT 3 (2026-09-23) with this scanner: 17 literal exec edges from listed shell and
workflow gate files reach 15 repo scripts, 9 of them unlisted (this screen among them); a plain text
grep, which also counts comments, strings and commands sent to the PC, finds 30 reaching 13
unlisted. Also not followed: other ways to run code in the process (other loader classes such as
SourcelessFileLoader, zipimport, runpy.run_module, pickle, ctypes, a loader reached through getattr
or globals(), a name rebound by exec'd text), and the spellings VERIFY-J1-0-R23-STAMP lists as
F-B3 and F-B4 (issue #37).
"""

import argparse
import ast
import bisect
import os
import posixpath
import re
import stat
import subprocess
import sys
from pathlib import Path

# A listed gate file must be a REGULAR file (contract AMENDMENT 1, VERIFY-J1-0-R1 R3):
# `git show :<path>` returns a symlink's LINK TEXT, so a listed path replaced by a symlink
# to an unlisted file screened clean. Only these index modes are accepted in --staged.
REGULAR_INDEX_MODES = frozenset(["100644", "100755"])

# ---------- Closed vocabulary ----------

# Simple tokens: matched as whole maximal runs of [A-Za-z0-9_-], case-insensitive.
# A maximal run is the longest contiguous sequence of identifier characters.
# "laya_probe" is ONE run and is NOT in the list, so it does not fire.
# "receives" is ONE run and is NOT in the list, so it does not fire.
# "Laya" matches "laya" case-insensitively and fires.
SIMPLE_TOKENS = frozenset([
    "laya", "systemone", "system_one", "system-one",
    "jev", "jevcache", "sieve", "sieve-run",
    "decide-harvest", "decide_harvest", "laya-decide",
])

# Dotted tokens: matched as literal substrings at identifier boundaries.
DOTTED_TOKENS = (
    "agent_factory.decisions",
    "decisions.ledger",
    "decisions.canonical",
    "decisions.jsonl",
)

# The screen's own path -- refuses to be listed (it contains the vocabulary).
SELF_PATH = "scripts/no_laya_in_gates.py"

# ---------- Include edges (AMENDMENT 2) ----------

# Third-party modules a Python gate may import. Closed: a new one is a reviewed change here.
# fubuki_os and lint come from S0-07's pinned fubuki-os checkout, outside this repo.
EXTERNAL_MODULES = frozenset(["fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"])

# Where a first-party import is looked for, besides the importing file's own directory
# and its subdirectories (to this depth).
IMPORT_SEARCH_DEPTH = 2
IMPORT_SEARCH_ROOTS = ("scripts", "src")

# The source edges a gate file may keep: (gate file, the exact target text). Closed: a new
# one is a reviewed change here. Both load no repo code: the first is the untracked bridge
# link file the owner pastes (KEY=VALUE lines), the second the dispatcher tests' fake-bridge seam.
ALLOWED_SOURCES = frozenset([
    ("scripts/pc_lane.sh", '"$ROOT/.pc-bridge.env"'),
    ("scripts/pc_lane.sh", '"$PC_LANE_BRIDGE_FN"'),
])

# A command segment that sources a file, read on the MASKED segment (quoted text replaced).
_SOURCE_RE = re.compile(r"^(?:source|\.)[ \t]+(\S.*)$")
_LEADING_KEYWORD_RE = re.compile(r"^(?:then|do|else|elif|if|while|until|!)[ \t]+")


def _is_python_gate(entry, content):
    """A listed file is Python when it ends in .py or its first line is a python shebang."""
    if entry.endswith(".py"):
        return True
    first = content.split("\n", 1)[0]
    return first.startswith("#!") and "python" in first


class _Open(Exception):
    """The scan cannot finish in sync: a construct is still open at the end of the text (R4-1), or a heredoc word
    holds an escape the scan does not translate (R5-1). The line it began on, and what it is."""

    def __init__(self, line, what):
        super().__init__(line, what)
        self.line = line
        self.what = what


# The words a segment may start with before its command word.
_LEADING_KEYWORDS = frozenset(["then", "do", "else", "elif", "if", "while", "until", "!"])
# The characters that end an unquoted word: bash's metacharacters.
_WORD_END = " \t\n;&|()<>"


def _unquote(word):
    """A heredoc word after quote removal (a delimiter is never expanded). A $'…' part is read as '…', which is
    right only without a backslash: heredoc() refuses a word holding $' and a backslash first (R5-1)."""
    out, quote, i = [], None, 0
    while i < len(word):
        c = word[i]
        if quote == "'":
            if c == "'":
                quote = None
            else:
                out.append(c)
        elif c == "\\" and (quote is None or word[i + 1:i + 2] in ('"', "\\", "$", "`")):
            out.append(word[i + 1:i + 2])
            i += 1
        elif c == '"' or (c == "'" and quote is None):
            quote = None if quote == c else c
        elif not (c == "$" and quote is None and word[i + 1:i + 2] in ("'", '"')):
            out.append(c)
        i += 1
    return "".join(out)


class _ShellScan:
    """Bash's lexical rules over one shell text, enough to list every command it runs (AMENDMENT 3, R4-2).

    Quotes ('…', "…", $'…', $"…"), expansions (${…}, $(…), $((…)), `…`, <(…), >(…)), comments, arithmetic
    ((( … )) and $(( … )), where << is a shift), case patterns and heredocs follow bash 5.2 (measured). A
    heredoc delimiter is a shell word (<<\\EOF, <<'EOF', <<-EOF, END-X); the body is data, except that an
    unquoted body expands $(…) and `…`, whose commands run. `segments` holds (lineno, raw, masked) per
    command, nested commands included; masked replaces quoted and expanded text with 'Q', so a word inside
    them never starts a command. A construct left open at the end of the text (R4-1), and a heredoc word
    holding $' and a backslash (R5-1), raise _Open."""

    def __init__(self, text, first_line=1):
        self.s = text
        self.i = 0
        self.first_line = first_line
        self.newlines = [k for k, c in enumerate(text) if c == "\n"]
        self.segments = []
        self.heredocs = []          # opened, body not read yet: (strip_tabs, delimiter, expands, line)
        self.not_arith = {}         # start of each (( or $(( attempt that failed -> None, or the heredocs it read (R5-2)
        self.bodies_read = 0        # read_bodies calls; an attempt that makes none reads no pending heredoc

    def line(self, pos):
        return self.first_line + bisect.bisect_left(self.newlines, pos)

    def scan(self):
        self.commands(None, None, 0)
        self.no_heredoc_pending()

    def no_heredoc_pending(self):
        if self.heredocs:
            raise _Open(self.heredocs[0][3], "heredoc <<%s pending" % self.heredocs[0][1])

    def commands(self, close, what, start):
        """Command text up to `close` (")" for $( … ) and <( … ); None: to the end of the text)."""
        s = self.s
        raw, masked, words = [], [], []
        seg_line = wstart = None
        depth = pat_depth = 0
        case = []                   # one entry per open case statement: "word", "pat" or "body"

        def end_word():
            nonlocal wstart
            if wstart is None:
                return
            word = "".join(masked[wstart:])
            wstart = None
            at_command = all(w in _LEADING_KEYWORDS for w in words)
            words.append(word)
            top = case[-1] if case else None
            if top == "word" and word == "in":
                case[-1] = "pat"
            elif top == "pat" and word == "esac" and not pat_depth:
                case.pop()
            elif top in (None, "body") and at_command and word == "case":
                case.append("word")
            elif top == "body" and at_command and word == "esac":
                case.pop()

        def flush():
            end_word()
            text = "".join(raw).strip()
            if text:
                self.segments.append((seg_line, text, "".join(masked).strip()))
            del raw[:], masked[:], words[:]

        def put(pos, quoted):
            """Add s[pos:self.i] to the current word, masked when it is quoted or expanded text."""
            nonlocal seg_line, wstart
            text = s[pos:self.i]
            if not raw:
                seg_line = self.line(pos)
            if wstart is None:
                wstart = len(masked)
            raw.append(text)
            masked.append("Q" * len(text) if quoted else text)

        while self.i < len(s):
            pos, c = self.i, s[self.i]
            nxt = s[pos + 1:pos + 2]
            if c == "\n":
                flush()
                self.i += 1
                self.read_bodies()
            elif c == "\\" and nxt == "\n":
                self.i += 2                 # a line continuation joins the two lines
            elif c in " \t":
                end_word()
                if raw:
                    raw.append(c)
                    masked.append(c)
                self.i += 1
            elif c == "#" and wstart is None:
                end = s.find("\n", pos)     # a comment: a '#' that starts a word
                self.i = len(s) if end < 0 else end
            elif c in ";&|":
                self.i += 1
                if c == ";" and nxt in (";", "&") and case and case[-1] == "body":
                    case[-1] = "pat"        # ;; ;& ;;& end a case clause
                    self.i += 2 if s.startswith(";;&", pos) else 1
                flush()
            elif c == "(" and case and case[-1] == "pat":
                self.i += 1
                if wstart is not None:      # an extglob group inside a pattern (else: the optional '(')
                    pat_depth += 1
                    put(pos, False)
            elif c == "(":
                end_word()
                if nxt == "(" and all(w in _LEADING_KEYWORDS or w == "for" for w in words) \
                        and self.arith(pos, 2, "(("):
                    put(pos, True)
                else:
                    self.i += 1
                    depth += 1
                    flush()
            elif c == ")":
                end_word()
                self.i += 1
                if case and case[-1] == "pat":
                    if pat_depth:
                        pat_depth -= 1
                        put(pos, False)
                        continue
                    case[-1] = "body"
                elif depth:
                    depth -= 1
                elif close is not None:
                    flush()
                    return
                flush()
            elif c in "{}" and wstart is None and (not nxt or nxt in _WORD_END):
                self.i += 1                 # the reserved words { and }; a brace inside a word is text
                flush()
            elif c in "<>" and nxt == "(":
                self.i += 2
                self.commands(")", c + "( unclosed", pos)
                put(pos, True)
            elif s.startswith("<<", pos) and not s.startswith("<<<", pos):
                end_word()
                self.heredoc(pos)
                put(pos, True)
                end_word()
            elif c in "<>":
                end_word()
                self.i += 3 if s.startswith("<<<", pos) else 1
                put(pos, False)
                end_word()
            else:
                self.step(False)
                put(pos, self.i - pos > 1 or c in "'\"`")
        if close is not None:
            raise _Open(self.line(start), what)
        flush()

    def step(self, in_dq):
        """Consume one quote, expansion, escape or plain character at self.i."""
        c = self.s[self.i]
        if c == "\\":
            self.i += 2
        elif c == "'" and not in_dq:
            self.squote()
        elif c == '"' and not in_dq:
            self.dq()
        elif c == "$":
            self.dollar(in_dq)
        elif c == "`":
            self.backtick()
        else:
            self.i += 1

    def dollar(self, in_dq):
        """Consume the $-construct at self.i ($(( … )), $( … ), ${ … }, $'…', $"…"), or a lone $."""
        s, start = self.s, self.i
        nxt = s[start + 1:start + 2]
        if s.startswith("$((", start) and self.arith(start, 3, "$(("):
            return
        if nxt == "(":
            self.i = start + 2
            self.commands(")", "$( unclosed", start)
        elif nxt == "{":
            self.brace(start)
        elif nxt == "'" and not in_dq:
            self.ansi(start)
        elif nxt == '"' and not in_dq:
            self.i = start + 1
            self.dq()
        else:
            self.i = start + 1

    def arith(self, start, skip, what):
        """(( … )) or $(( … )), where << is a shift. False, with nothing consumed, when a ')' that does not
        close the pair shows the text is a subshell after all (bash reads `$( (a) | b )` that way).
        The decision is made once per start (R5-2). The caller re-scans a failed attempt's text as commands, and
        without a memo each enclosing failed attempt re-ran this one: `$(( $(( … ) ) ) )` nested k deep cost 2^k.
        Besides the text, the pending heredocs are the only state an attempt reads, and only through read_bodies
        (a newline inside a nested $( … )). So a remembered failure that read no heredoc body holds under any
        pending heredocs; one that read some holds under the same ones, and under others it is refused (fail
        closed), never re-run: a re-run per state was 2^k again (a <<W in each level is a shift in the attempt
        and a heredoc in the re-scan). A success is not remembered: its re-scan re-adds the segments that the
        enclosing failure deleted."""
        s = self.s
        pending = tuple(self.heredocs)
        if start in self.not_arith:
            if self.not_arith[start] in (None, pending):
                return False
            raise _Open(self.line(start), what + " re-read with other heredocs pending")
        kept, reads = (len(self.segments), list(self.heredocs)), self.bodies_read
        self.i = start + skip
        depth = 0
        while self.i < len(s):
            c = s[self.i]
            if c == ")" and not depth:
                if s.startswith("))", self.i):
                    self.i += 2
                    return True
                del self.segments[kept[0]:]
                self.heredocs[:] = kept[1]
                self.i = start
                self.not_arith[start] = None if self.bodies_read == reads else pending
                return False
            if c in "()":
                depth += 1 if c == "(" else -1
                self.i += 1
            else:
                self.step(False)
        raise _Open(self.line(start), what + " unclosed")

    def brace(self, start):
        """${ … }: quotes and nested expansions count; a bare { does not nest (bash 5.2, measured)."""
        s = self.s
        self.i = start + 2
        while self.i < len(s):
            if s[self.i] == "}":
                self.i += 1
                return
            self.step(False)
        raise _Open(self.line(start), "${ unclosed")

    def dq(self):
        """A double-quoted string; self.i is at its opening quote."""
        s, start = self.s, self.i
        self.i += 1
        while self.i < len(s):
            if s[self.i] == '"':
                self.i += 1
                return
            self.step(True)
        raise _Open(self.line(start), 'quote " open')

    def squote(self):
        end = self.s.find("'", self.i + 1)
        if end < 0:
            raise _Open(self.line(self.i), "quote ' open")
        self.i = end + 1

    def ansi(self, start):
        """$'…', where a backslash escapes the next character (\\' included)."""
        s = self.s
        self.i = start + 2
        while self.i < len(s):
            c = s[self.i]
            self.i += 2 if c == "\\" else 1
            if c == "'":
                return
        raise _Open(self.line(start), "quote $' open")

    def backtick(self):
        """`…`: bash ends it at the first unescaped backquote (quotes do not count, measured) and runs the
        text inside, with \\$ \\` \\\\ unescaped, as commands."""
        s, start = self.s, self.i
        inner, j = [], start + 1
        while j < len(s) and s[j] != "`":
            if s[j] == "\\" and j + 1 < len(s):
                inner.append(s[j + 1] if s[j + 1] in "$`\\" else s[j:j + 2])
                j += 2
            else:
                inner.append(s[j])
                j += 1
        if j >= len(s):
            raise _Open(self.line(start), "` unclosed")
        self.i = j + 1
        sub = _ShellScan("".join(inner), self.line(start))
        sub.scan()
        self.segments.extend(sub.segments)

    def heredoc(self, start):
        """<<[-]WORD: the delimiter is WORD after quote removal, and a quoted WORD keeps the body from
        expanding. The body is read at the next newline (read_bodies). A WORD holding $' and a backslash is
        refused (R5-1, V-01): bash translates the ANSI-C escape ($'echo \\x41' ends the body at `echo A`) and
        _unquote does not, so the scan and bash would end the body at different lines, and a command bash runs
        could be read as data."""
        s = self.s
        self.i = start + 2
        strip = s.startswith("-", self.i)
        if strip:
            self.i += 1
        while self.i < len(s) and s[self.i] in " \t":
            self.i += 1
        begin = self.i
        while self.i < len(s) and s[self.i] not in _WORD_END:
            self.step(False)
        word = s[begin:self.i]
        if not word:
            raise _Open(self.line(start), "heredoc << without a delimiter")
        if "$'" in word and "\\" in word:
            raise _Open(self.line(start), "heredoc <<%s: $'...' escape not translated" % word)
        quoted = any(q in word for q in "'\"\\")
        self.heredocs.append((strip, _unquote(word), not quoted, self.line(start)))

    def read_bodies(self):
        """Read the bodies of the heredocs opened on the line that just ended (self.i is past its newline). Every
        call is counted, even one with nothing pending: the same newline reached with a heredoc pending reads it."""
        s = self.s
        self.bodies_read += 1
        while self.heredocs:
            strip, delim, expands, line = self.heredocs.pop(0)
            body = self.i
            while True:
                if self.i >= len(s):
                    raise _Open(line, "heredoc <<%s pending" % delim)
                end = s.find("\n", self.i)
                end = len(s) if end < 0 else end
                at, self.i = self.i, end + 1
                if (s[at:end].lstrip("\t") if strip else s[at:end]) == delim:
                    break
            if expands:
                sub = _ShellScan(s[body:at], self.line(body))
                while sub.i < len(sub.s):
                    sub.step(True)
                sub.no_heredoc_pending()
                self.segments.extend(sub.segments)


def _command_segments(content, first_line=1):
    """(segments, opened) for one shell text: segments = [(lineno, raw, masked)] in line order, commands
    nested in $( ), ` `, <( ) and unquoted heredoc bodies included; opened = (line, what) when the scan
    cannot finish in sync (_Open: R4-1, R5-1; or nesting too deep), else None."""
    scan = _ShellScan(content, first_line)
    opened = None
    try:
        scan.scan()
    except _Open as e:
        opened = (e.line, e.what)
    except RecursionError:
        opened = (first_line, "constructs nested too deep to scan")
    return sorted(scan.segments, key=lambda seg: seg[0]), opened


def _workflow_runs(content):
    """(first line, text, literal) of every scalar `run:` value in a workflow file, in line order; None when the
    file does not parse (R4-3). The first line is read from the value's own scalar token, never from the node's
    start, which is its first property (an &anchor or a !!tag) and can sit on an earlier line (R6): the line after
    the indicator of a block (| or >), else the line of a plain or quoted scalar's first character. Only a literal
    block (|) keeps every line break, so a refusal in it names its own line; a plain, quoted or folded value joins
    or escapes some of its line breaks, so its lines do not map back to the file's and every refusal in it names
    the first line (R5-4)."""
    try:
        import yaml
    except ImportError:
        print("no_laya_in_gates: PyYAML is not importable, so no workflow file can be proven", file=sys.stderr)
        return None
    try:
        stack = list(yaml.compose_all(content, Loader=yaml.SafeLoader))
        # a scalar node ends where its token ends; an empty value has no token and nothing to refuse
        token_line = {t.end_mark.index: t.start_mark.line for t in yaml.scan(content, Loader=yaml.SafeLoader)
                      if isinstance(t, yaml.ScalarToken)}
    except yaml.YAMLError:
        return None
    runs, seen = [], set()
    while stack:
        node = stack.pop()
        if node is None or id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, yaml.MappingNode):
            for key, value in node.value:
                if isinstance(key, yaml.ScalarNode) and key.value == "run" and isinstance(value, yaml.ScalarNode):
                    line = token_line.get(value.end_mark.index, value.start_mark.line)
                    runs.append((line + (2 if value.style in ("|", ">") else 1), value.value, value.style == "|"))
                stack += [key, value]
        elif isinstance(node, yaml.SequenceNode):
            stack += node.value
    return sorted(runs)


def _source_errors(entry, content):
    """`gate-file-sources` lines for every command that sources a file, unless the exact (file, target)
    pair is in ALLOWED_SOURCES; `gate-file-unparseable` when the scan cannot reach the end of a text in
    sync (R4-1, R5-1) or a workflow file does not parse (R4-3). A workflow's run: values are scanned one by
    one, each refusal at the line _workflow_runs maps it to (R5-4)."""
    if entry.endswith((".yml", ".yaml")):
        texts = _workflow_runs(content)
        if texts is None:
            return ["gate-file-unparseable: %s" % entry]
    else:
        texts = [(1, content, True)]
    errors = []
    for first_line, text, by_line in texts:
        segments, opened = _command_segments(text, first_line)
        for lineno, raw, masked in segments:
            cut = 0
            while True:
                m = _LEADING_KEYWORD_RE.match(masked[cut:])
                if not m:
                    break
                cut += m.end()
            m = _SOURCE_RE.match(masked[cut:])
            if not m:
                continue
            target = raw[cut + m.start(1):].strip()
            if (entry, target) in ALLOWED_SOURCES:
                continue
            errors.append("gate-file-sources: %s:%d: %s" % (entry, lineno if by_line else first_line, target))
        if opened:
            errors.append("gate-file-unparseable: %s:%d: %s" % (entry, opened[0] if by_line else first_line, opened[1]))
    return errors


class _Tree:
    """The files an import can resolve to: the git index (--staged) or the filesystem."""

    def __init__(self, root, staged):
        self.root = root
        self.staged = staged
        self.index = None
        self.dirs = None
        self._subdirs = {}
        if staged:
            r = subprocess.run(["git", "ls-files", "-z", "--cached"],
                               capture_output=True, check=True)
            self.index = set(p.decode("utf-8", "replace") for p in r.stdout.split(b"\0") if p)
            self.dirs = set()
            for path in self.index:
                parent = posixpath.dirname(path)
                while parent and parent not in self.dirs:
                    self.dirs.add(parent)
                    parent = posixpath.dirname(parent)

    def isfile(self, rel):
        if self.staged:
            return rel in self.index
        return (self.root / rel).is_file()

    def subdirs(self, rel_dir, depth):
        """Directories below rel_dir, at most `depth` levels down, hidden ones skipped; sorted."""
        key = (rel_dir, depth)
        if key not in self._subdirs:
            self._subdirs[key] = self._scan_subdirs(rel_dir, depth)
        return self._subdirs[key]

    def _scan_subdirs(self, rel_dir, depth):
        prefix = rel_dir + "/" if rel_dir else ""
        found = set()
        if self.staged:
            for d in self.dirs:
                if not d.startswith(prefix) or d == rel_dir:
                    continue
                parts = d[len(prefix):].split("/")
                if len(parts) <= depth and not any(p.startswith(".") for p in parts):
                    found.add(d)
        else:
            def walk(abs_dir, rel, level):
                if level > depth:
                    return
                try:
                    children = sorted(os.scandir(abs_dir), key=lambda e: e.name)
                except OSError:
                    return
                for child in children:
                    if child.name.startswith(".") or not child.is_dir(follow_symlinks=False):
                        continue
                    child_rel = rel + "/" + child.name if rel else child.name
                    found.add(child_rel)
                    walk(child.path, child_rel, level + 1)
            walk(self.root / rel_dir if rel_dir else self.root, rel_dir, 1)
        return sorted(found)


def _package_files(tree, base, parts, names):
    """Files a dotted import reaches from package dir `base`: each package __init__.py, then the
    module file, then any imported name that is itself a submodule. None when the first part is
    not found."""
    files = []
    cur = base
    for i, part in enumerate(parts):
        pkg_init = posixpath.join(cur, part, "__init__.py")
        mod = posixpath.join(cur, part + ".py")
        if tree.isfile(pkg_init):
            cur = posixpath.join(cur, part)
            files.append(pkg_init)
        elif tree.isfile(mod):
            files.append(mod)
            return files
        else:
            return files if i else None
    for name in names:
        sub_mod = posixpath.join(cur, name + ".py")
        sub_pkg = posixpath.join(cur, name, "__init__.py")
        if tree.isfile(sub_mod):
            files.append(sub_mod)
        elif tree.isfile(sub_pkg):
            files.append(sub_pkg)
    return files


def _flagged_by_vocabulary(entry, module, names):
    """Imports the vocabulary scan already reports (exit 3) are not also resolved here."""
    if not entry.endswith(".py"):
        return False
    return (module == "agent_factory.decisions"
            or module.startswith("agent_factory.decisions.")
            or (module == "agent_factory" and "decisions" in names))


def _import_errors(entry, content, tree, listed_set):
    """Completeness lines for the imports of one Python gate file."""
    try:
        parsed = ast.parse(content)
    except SyntaxError:
        return ["gate-file-unparseable: %s" % entry]
    imports = []
    nodes = list(ast.walk(parsed))
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, 0, alias.name, ()))
        elif isinstance(node, ast.ImportFrom):
            imports.append((node.lineno, node.level, node.module or "",
                            tuple(a.name for a in node.names)))
    importer_dir = posixpath.dirname(entry)
    errors = []
    for lineno, level, module, names in sorted(imports):
        if _flagged_by_vocabulary(entry, module, names):
            continue
        label = ("." * level) + (module or ",".join(names))
        if level:
            base = importer_dir
            for _ in range(level - 1):
                base = posixpath.dirname(base)
            parts = module.split(".") if module else []
            files = _package_files(tree, base, parts, names)
            if not files and not parts and tree.isfile(posixpath.join(base, "__init__.py")):
                files = [posixpath.join(base, "__init__.py")]
            if not files:
                errors.append("gate-file-import-unresolved: %s:%d imports %s" % (entry, lineno, label))
                continue
        else:
            parts = module.split(".")
            candidates = _module_candidates(tree, importer_dir, module)
            if not candidates:
                top = parts[0]
                if top in sys.stdlib_module_names or top == "__future__" or top in EXTERNAL_MODULES:
                    continue
                errors.append("gate-file-import-unresolved: %s:%d imports %s" % (entry, lineno, module))
                continue
            if len(candidates) > 1:
                where = ",".join(_package_files(tree, d, parts[:1], ())[0] for d in candidates)
                errors.append("gate-file-import-ambiguous: %s:%d imports %s -> %s" % (entry, lineno, module, where))
                continue
            files = _package_files(tree, candidates[0], parts, names)
        for path in files:
            if path not in listed_set:
                errors.append("gate-file-import-unlisted: %s:%d imports %s -> %s" % (entry, lineno, label, path))
    return errors + _load_errors(entry, parsed, tree, listed_set, nodes)


# ---------- Dynamic in-process loads (AMENDMENT 3, R4-4) ----------

# Calls that load another file's code into the gate's own process: name -> (position and keyword of the
# argument naming what is loaded, what that argument is). exec, eval and compile count only as the builtins;
# text written in the gate itself is a load only when it imports or loads something in turn.
_LOADERS = {
    "spec_from_file_location": (1, "location", "path"),
    "SourceFileLoader": (1, "path", "path"),
    "run_path": (0, "path_name", "path"),
    "import_module": (0, "name", "module"),
    "__import__": (0, "name", "module"),
    "exec": (0, "source", "text"),
    "eval": (0, "source", "text"),
    "compile": (0, "source", "text"),
}

# Dynamic loads whose target static resolution cannot prove: (gate file, literal repo path) -> how many load
# sites in that gate file may name that path joined to an unresolved base directory. More such sites than the
# count are all refused, and the path must itself be listed. An entry binds only the gate file, the literal
# path and the site count. The base directory is not bound: a site whose base is re-pointed (an environment
# value, another directory) still matches, and a wrapper that runs one site twice makes a second load that
# counts once. Both are outside this check (F-B5's class, issue #37). Closed: a new entry is a reviewed change here.
ALLOWED_DYNAMIC_LOADS = {
    ("scripts/lint_delta.py", ".claude/hooks/edit-snapshot.py"): 1,   # base: git rev-parse --show-toplevel
    ("scripts/proof-runner", "scripts/validate-ledger"): 1,          # base: the --root argument
    ("scripts/ledger-gen", "scripts/validate-ledger"): 1,            # base: the --root argument
}

# What the resolver cannot tell: an unknown directory, no known path under it.
_UNKNOWN = ("under", "")
_PATH_TYPES = frozenset(["pathlib.Path", "pathlib.PurePath", "pathlib.PosixPath", "pathlib.PurePosixPath"])


def _norm(kind, path):
    """A normalized path value; None when a repo path climbs above the repo root."""
    parts = [p for p in posixpath.normpath(path or ".").split("/") if p != "."]
    while parts and parts[0] == "..":
        if kind == "at":
            return None
        parts.pop(0)                    # an unknown directory absorbs the climb
    return (kind, "/".join(parts))


def _as_path(value):
    """A value used as a path. A relative string is taken against the working directory, the repo root
    (the hook and CI run the gates there); an absolute one is outside what the screen can map."""
    if value is None or value[0] != "str":
        return value
    return None if value[1].startswith("/") else _norm("at", value[1])


def _join(left, right):
    """left / right as pathlib and os.path.join do it: an absolute right side replaces the left."""
    if left is None or right is None:
        return None
    if right[0] != "str":
        return right
    if right[1].startswith("/"):
        return None
    if left[0] == "str":
        return ("str", posixpath.join(left[1], right[1]))
    return _norm(left[0], posixpath.join(left[1], right[1]))


def _parent(value, times=1):
    """pathlib's .parent and os.path.dirname, `times` times. A relative string stays relative; one that is
    absolute or not normalized ('./a', 'a/', 'a/../b', where the two disagree) cannot be told."""
    for _ in range(times):
        if value is None or value == ("at", ""):
            return None                 # the repo root's parent is outside the repo
        if value[0] == "str" and (value[1].startswith("/") or posixpath.normpath(value[1] or ".") != (value[1] or ".")):
            return None
        value = (value[0], posixpath.dirname(value[1]))
    return value


def _with_name(value, name):
    """pathlib's .with_name: the parent joined to a new final name."""
    if value in (None, ("at", ""), ("str", "")) or name is None or name[0] != "str" or not name[1] or "/" in name[1]:
        return None
    return _join(_parent(value), name)


class _Resolver:
    """Static values of the path and string expressions of one parsed Python gate file (R4-4).

    A value is ("str", text), ("at", path under the repo root), ("under", path under an unknown directory)
    or None (a path outside the repo). Followed: literals, Path(__file__) chains, pathlib and os.path calls,
    names bound by plain assignment in the module or a function, and a parameter through the arguments of
    the function's own direct calls in the file. Anything else is _UNKNOWN."""

    def __init__(self, entry, parsed, aliases):
        self.entry = entry
        self.bound = {}             # (id of the scope node, None for the module; name) -> bindings
        self.defs = {}              # function name -> [(def node, scope)]
        self.calls = {}             # function name -> [(call node, scope)]: calls that name it directly
        self.reads = {}             # name -> how many times it is read
        self.sites = []             # (node, scope, loader name) for every use of a loader
        self.aliases = aliases      # local name -> loader (`from importlib.util import X as local`)
        self.active = set()
        self.star_import = False    # `from x import *` can rebind any module-level name
        self._assigned = set()
        self._walk(parsed, ())

    def _bind(self, scope, name, how):
        self.bound.setdefault((id(scope[-1]) if scope else None, name), []).append(how)

    def _loader(self, node):
        return _loader_name(node, self.aliases)

    def _walk(self, node, scope):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            inner = scope + (node,)
            if not isinstance(node, ast.Lambda):
                self._bind(scope, node.name, ("other",))
                self.defs.setdefault(node.name, []).append((node, scope))
            a = node.args
            for arg in a.posonlyargs + a.args + a.kwonlyargs + [a.vararg, a.kwarg]:
                if arg is not None:
                    self._bind(inner, arg.arg, ("param", node))
            outer = a.defaults + [d for d in a.kw_defaults if d is not None] + getattr(node, "decorator_list", [])
            outer += [x.annotation for x in a.posonlyargs + a.args + a.kwonlyargs + [a.vararg, a.kwarg]
                      if x is not None and x.annotation is not None]
            outer += [node.returns] if getattr(node, "returns", None) is not None else []
            for child in outer:         # evaluated where the function is defined
                self._walk(child, scope)
            for child in node.body if isinstance(node.body, list) else [node.body]:
                self._walk(child, inner)
            return
        if isinstance(node, ast.ClassDef):
            self._bind(scope, node.name, ("other",))
            for child in node.bases + node.keywords + node.decorator_list:
                self._walk(child, scope)
            for child in node.body:
                self._walk(child, scope + (node,))
            return
        if isinstance(node, ast.Call):
            loader = self._loader(node.func)
            if loader:
                self.sites.append((node, scope, loader))
            children = node.args + node.keywords
            if isinstance(node.func, ast.Name):
                self.calls.setdefault(node.func.id, []).append((node, scope))
                self.reads[node.func.id] = self.reads.get(node.func.id, 0) + 1
            else:
                children = [node.func.value if isinstance(node.func, ast.Attribute) else node.func] + children
            for child in children:
                self._walk(child, scope)
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                if isinstance(target, ast.Name):
                    self._assigned.add(id(target))
                    self._bind(scope, target.id, ("expr", node.value, scope))
        elif isinstance(node, ast.Import):
            for a in node.names:
                self._bind(scope, a.asname or a.name.split(".")[0], ("import", a.name if a.asname else a.name.split(".")[0], None))
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                self.star_import = self.star_import or a.name == "*"
                self._bind(scope, a.asname or a.name, ("import", ("." * node.level) + (node.module or ""), a.name))
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            # the name can be rebound in the module (global) or an enclosing function (nonlocal) from here
            outer = [()] if isinstance(node, ast.Global) else [scope[:k] for k in range(1, len(scope))]
            for name in node.names:
                for where in [scope] + outer:
                    self._bind(where, name, ("other",))
        elif isinstance(node, ast.ExceptHandler) and node.name:
            self._bind(scope, node.name, ("other",))
        elif type(node).__name__ in ("MatchAs", "MatchStar", "MatchMapping"):
            name = getattr(node, "rest", None) if type(node).__name__ == "MatchMapping" else node.name
            if name:
                self._bind(scope, name, ("other",))
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                self.reads[node.id] = self.reads.get(node.id, 0) + 1
                if self._loader(node):              # a loader read without being called
                    self.sites.append((node, scope, self._loader(node)))
            elif id(node) not in self._assigned:    # a for, with, walrus, del or augmented target
                self._bind(scope, node.id, ("other",))
        elif isinstance(node, ast.Attribute) and self._loader(node):
            self.sites.append((node, scope, self._loader(node)))
        for child in ast.iter_child_nodes(node):
            self._walk(child, scope)

    def _chain(self, scope):
        """The scopes a name read in `scope` is found in: its own, the enclosing functions, the module."""
        inner = [id(scope[-1])] if scope else []
        return inner + [id(s) for s in reversed(scope[:-1]) if not isinstance(s, ast.ClassDef)] + [None]

    def name_values(self, name, scope):
        for owner in self._chain(scope):
            bindings = self.bound.get((owner, name))
            if bindings is None:
                continue
            if (owner, name) in self.active:
                return [_UNKNOWN]
            self.active.add((owner, name))
            try:
                values = []
                for how in bindings:
                    if how[0] == "expr":
                        values += self.values(how[1], how[2])
                    elif how[0] == "param":
                        values += self.param_values(how[1], name)
                    else:
                        values.append(_UNKNOWN)
                return values + ([_UNKNOWN] if owner is None and self.star_import else [])
            finally:
                self.active.discard((owner, name))
        return [("at", self.entry)] if name == "__file__" and not self.star_import else [_UNKNOWN]

    def dotted(self, node, scope):
        """What a Name or Attribute refers to through the file's imports ("os.path.join", "pathlib.Path"), a
        builtin as "builtins.<name>", or None when a name is bound any other way."""
        if isinstance(node, ast.Attribute):
            base = self.dotted(node.value, scope)
            return base and base + "." + node.attr
        if not isinstance(node, ast.Name):
            return None
        for owner in self._chain(scope):
            bindings = self.bound.get((owner, node.id))
            if bindings is not None:
                refs = set(how[1] + ("." + how[2] if how[2] else "") if how[0] == "import" else None
                           for how in bindings)
                return refs.pop() if len(refs) == 1 else None
        return None if self.star_import else "builtins." + node.id

    def param_values(self, func, name):
        """What a parameter holds: the arguments that the function's direct calls in this file pass.
        Unknown for a lambda or a method, a function defined twice, or one read other than by a call."""
        fname = getattr(func, "name", None)
        defs, calls = self.defs.get(fname, []), self.calls.get(fname, [])
        if (len(defs) != 1 or (defs[0][1] and isinstance(defs[0][1][-1], ast.ClassDef)) or not calls
                or defs[0][0].decorator_list or self.reads.get(fname) != len(calls)):
            return [_UNKNOWN]
        a = func.args
        positional = [arg.arg for arg in a.posonlyargs + a.args]
        defaults = dict(zip(positional[len(positional) - len(a.defaults):], a.defaults))
        defaults.update((arg.arg, d) for arg, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None)
        values = []
        for call, where in calls:
            if any(isinstance(x, ast.Starred) for x in call.args) or any(k.arg is None for k in call.keywords):
                return [_UNKNOWN]
            given = [k.value for k in call.keywords if k.arg == name]
            if not given and name in positional and positional.index(name) < len(call.args):
                given = [call.args[positional.index(name)]]
            if given:
                values += self.values(given[0], where)
            elif name in defaults:
                values += self.values(defaults[name], defs[0][1])
            else:
                return [_UNKNOWN]
        return values

    def values(self, node, scope):
        """The values expression `node` can take, read in `scope`."""
        if isinstance(node, ast.Constant):
            return [("str", node.value)] if isinstance(node.value, str) else [None]
        if isinstance(node, ast.Name):
            return self.name_values(node.id, scope)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return [_join(a, b) for a in self.values(node.left, scope) for b in self.values(node.right, scope)]
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            return [_parent(v) for v in self.values(node.value, scope)]
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute)
                and node.value.attr == "parents" and isinstance(node.slice, ast.Constant)
                and type(node.slice.value) is int and node.slice.value >= 0):
            return [_parent(v, node.slice.value + 1) for v in self.values(node.value.value, scope)]
        if isinstance(node, ast.Call) and not node.keywords and not any(isinstance(a, ast.Starred) for a in node.args):
            return self.call_values(node, scope)
        if isinstance(node, ast.IfExp):
            return self.values(node.body, scope) + self.values(node.orelse, scope)
        if isinstance(node, ast.BoolOp):
            return [v for x in node.values for v in self.values(x, scope)]
        return [_UNKNOWN]

    def call_values(self, node, scope):
        f, args = node.func, node.args
        ref = self.dotted(f, scope) or ""
        method = f.attr if isinstance(f, ast.Attribute) and not ref else None     # a call on a value
        if ref in _PATH_TYPES or ref in ("os.path.join", "posixpath.join"):
            values, parts = (self.values(args[0], scope) if args else [("str", "")]), args[1:]
        elif method == "joinpath":
            values, parts = self.values(f.value, scope), args
        else:
            values = parts = None
        if values is not None:
            for part in parts:
                values = [_join(a, b) for a in values for b in self.values(part, scope)]
            return values
        if len(args) == 1 and ref in ("builtins.str", "os.fspath", "os.path.normpath", "posixpath.normpath"):
            return self.values(args[0], scope)
        if len(args) == 1 and ref in ("os.path.abspath", "os.path.realpath", "posixpath.abspath", "posixpath.realpath"):
            return [_as_path(v) for v in self.values(args[0], scope)]
        if len(args) == 1 and ref in ("os.path.dirname", "posixpath.dirname"):
            return [_parent(v) for v in self.values(args[0], scope)]
        if method in ("resolve", "absolute") and not args:
            return [_as_path(v) for v in self.values(f.value, scope)]
        if method == "with_name" and len(args) == 1:
            return [_with_name(v, n) for v in self.values(f.value, scope) for n in self.values(args[0], scope)]
        return [_UNKNOWN]

    def text_values(self, node, scope):
        """Where a text passed to exec, eval or compile comes from: ("code", text) when it is written in the
        gate itself, [] for the code object of another compile() load, else the file it was read from."""
        if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
            return [("code", node.value)]
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == "compile":
                return []
            if isinstance(f, ast.Attribute) and f.attr in ("read_text", "read_bytes") and not node.args:
                return self.values(f.value, scope)
            if (isinstance(f, ast.Attribute) and f.attr == "read" and isinstance(f.value, ast.Call)
                    and self.dotted(f.value.func, scope) in ("builtins.open", "io.open", "codecs.open")
                    and f.value.args):
                return self.values(f.value.args[0], scope)
        if isinstance(node, ast.Name):
            for owner in self._chain(scope):
                bindings = self.bound.get((owner, node.id))
                if bindings is None:
                    continue
                if (owner, node.id) in self.active or any(how[0] != "expr" for how in bindings):
                    return [None]
                self.active.add((owner, node.id))
                try:
                    return [v for how in bindings for v in self.text_values(how[1], how[2])]
                finally:
                    self.active.discard((owner, node.id))
        return [None]


def _loader_name(node, aliases):
    """The loader a Name or Attribute node names, or None (exec, eval and compile count only as builtins)."""
    if isinstance(node, ast.Name):
        name = aliases.get(node.id, node.id)
    elif isinstance(node, ast.Attribute) and (node.attr not in ("exec", "eval", "compile") or (
            isinstance(node.value, ast.Name) and node.value.id == "builtins")):
        name = node.attr
    else:
        return None
    return name if name in _LOADERS else None


def _load_sites(entry, parsed, nodes=None):
    """(line, kind, values) for each dynamic load in one parsed Python gate file (R4-4): kind is "path",
    "module" or "text"; values are what the resolver can tell about what the load reaches. `nodes` is the
    tree's ast.walk when the caller already has it."""
    aliases, used = {}, False
    for n in ast.walk(parsed) if nodes is None else nodes:
        if isinstance(n, ast.ImportFrom):
            aliases.update((a.asname, a.name) for a in n.names if a.name in _LOADERS and a.asname)
        used = used or _loader_name(n, {}) is not None
    if not used and not aliases:
        return []
    resolver = _Resolver(entry, parsed, aliases)
    sites = []
    for node, scope, loader in resolver.sites:
        position, keyword, kind = _LOADERS[loader]
        arg = None
        if isinstance(node, ast.Call):
            arg = next((k.value for k in node.keywords if k.arg == keyword), None)
            if arg is None and len(node.args) > position and not any(
                    isinstance(a, ast.Starred) for a in node.args[:position + 1]):
                arg = node.args[position]
        if loader == "__import__" and isinstance(node, ast.Call):
            level = next((k.value for k in node.keywords if k.arg == "level"), None)
            if level is None and len(node.args) > 4:
                level = node.args[4]
            if level is not None and not (isinstance(level, ast.Constant) and level.value == 0):
                arg = None                  # a relative __import__: the package is a runtime value
        if arg is None:
            values = [None]
        elif kind == "text":
            values = resolver.text_values(arg, scope)
        else:
            values = resolver.values(arg, scope)
        sites.append((node.lineno, kind, values))
    return sites


def _inert(code):
    """Code written into the gate as a string is part of the gate (its text is screened) unless it imports or
    loads something in turn, or does not parse."""
    try:
        parsed = ast.parse(code)
    except (SyntaxError, ValueError):
        return False
    return not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(parsed)) \
        and not _load_sites("", parsed)


def _module_candidates(tree, importer_dir, module):
    """The search directories in which the first part of an absolute import is a repo file (AMENDMENT 2)."""
    parts = module.split(".")
    search = [importer_dir] + tree.subdirs(importer_dir, IMPORT_SEARCH_DEPTH)
    search += [d for d in IMPORT_SEARCH_ROOTS if d not in search]
    return [d for d in search if _package_files(tree, d, parts[:1], ())]


def _load_errors(entry, parsed, tree, listed_set, nodes=None):
    """Completeness lines for the dynamic loads of one Python gate file (R4-4): each load reaches a listed
    file (a module name may also be stdlib or EXTERNAL_MODULES, exactly as a static import), or is one of
    the ALLOWED_DYNAMIC_LOADS within its count, or is refused."""
    importer_dir = posixpath.dirname(entry)
    found, uses = [], {}
    for index, (line, kind, values) in enumerate(_load_sites(entry, parsed, nodes)):
        unresolved, unlisted = False, set()
        for value in values:
            if kind == "module":
                module = value[1] if value is not None and value[0] == "str" else ""
                if not module or module.startswith("."):
                    unresolved = True
                elif not _flagged_by_vocabulary(entry, module, ()):
                    candidates = _module_candidates(tree, importer_dir, module)
                    if len(candidates) == 1:
                        unlisted.update(p for p in _package_files(tree, candidates[0], module.split("."), ())
                                        if p not in listed_set)
                    elif candidates or not (module.split(".")[0] in sys.stdlib_module_names
                                            or module.split(".")[0] in ("__future__",) + tuple(EXTERNAL_MODULES)):
                        unresolved = True
                continue
            value = _as_path(value)
            if value is None:
                unresolved = True
            elif value[0] == "code":
                unresolved = unresolved or not _inert(value[1])
            elif value[0] == "at":
                if value[1] not in listed_set:
                    if tree.isfile(value[1]):
                        unlisted.add(value[1])
                    else:
                        unresolved = True
            elif (entry, value[1]) in ALLOWED_DYNAMIC_LOADS:
                uses.setdefault((entry, value[1]), set()).add(index)
                if value[1] not in listed_set:
                    unlisted.add(value[1])
            else:
                unresolved = True
        found.append([line, unresolved, unlisted])
    for key, indexes in uses.items():
        if len(indexes) > ALLOWED_DYNAMIC_LOADS[key]:
            for index in indexes:
                found[index][1] = True
    errors = []
    for line, unresolved, unlisted in sorted(found, key=lambda site: site[0]):
        errors += ["gate-file-import-unlisted: %s:%d loads %s" % (entry, line, p) for p in sorted(unlisted)]
        if unresolved:
            errors.append("gate-file-import-unresolved: %s:%d" % (entry, line))
    return errors

# ---------- Matching ----------

_TOKEN_RE = re.compile(r"[A-Za-z0-9_-]+")
_ID_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

# Structural import patterns for .py files.
_IMPORT_RE = re.compile(
    r"^\s*(?:"
    r"import\s+agent_factory\.decisions\b"
    r"|from\s+agent_factory\.decisions(?:\.\w+)*\s+import\b"
    r"|from\s+agent_factory\s+import\s+decisions\b"
    r")",
)


def _check_line(line, is_py):
    """Return a list of matched vocabulary tokens from a single line."""
    hits = []
    seen = set()

    # 1. Simple tokens via maximal-run boundary matching
    for m in _TOKEN_RE.finditer(line):
        canon = m.group().lower()
        if canon in SIMPLE_TOKENS and canon not in seen:
            hits.append(canon)
            seen.add(canon)

    # 2. Dotted tokens via literal substring with boundary checks
    lower = line.lower()
    for tok in DOTTED_TOKENS:
        if tok in seen:
            continue
        idx = 0
        while True:
            pos = lower.find(tok, idx)
            if pos == -1:
                break
            before_ok = pos == 0 or lower[pos - 1] not in _ID_CHARS
            end = pos + len(tok)
            after_ok = end >= len(lower) or lower[end] not in _ID_CHARS
            if before_ok and after_ok:
                hits.append(tok)
                seen.add(tok)
                break
            idx = pos + 1

    # 3. Structural import check (.py files only)
    if is_py and "agent_factory.decisions" not in seen:
        if _IMPORT_RE.match(line):
            hits.append("agent_factory.decisions")

    return hits


# ---------- File reading ----------

def _read_staged(path):
    """Read the staged (index) version of a file via git show."""
    try:
        r = subprocess.run(
            ["git", "show", ":%s" % path],
            capture_output=True, text=True, check=True,
        )
        return r.stdout
    except subprocess.CalledProcessError:
        return None


def _read_file(root, path):
    """Read a file from a filesystem root."""
    fp = root / path
    try:
        return fp.read_text(errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


# ---------- Allowlist and completeness ----------

def _parse_allowlist(text):
    """Parse allowlist text, stripping comments and blanks."""
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries


def _load_allowlist(list_path):
    """Load the gate-file allowlist from a file path."""
    return _parse_allowlist(list_path.read_text())


def _glob_structural(root):
    """Walk the three structural patterns and return repo-relative paths."""
    found = set()
    # scripts/hooks/*
    hooks_dir = root / "scripts" / "hooks"
    if hooks_dir.is_dir():
        for p in hooks_dir.iterdir():
            if p.is_file():
                found.add(str(p.relative_to(root)))
    # .github/workflows/*.yml
    wf_dir = root / ".github" / "workflows"
    if wf_dir.is_dir():
        for p in wf_dir.glob("*.yml"):
            if p.is_file():
                found.add(str(p.relative_to(root)))
    # proofs/*/check_*.py
    proofs_dir = root / "proofs"
    if proofs_dir.is_dir():
        for sub in proofs_dir.iterdir():
            if sub.is_dir():
                for p in sub.glob("check_*.py"):
                    if p.is_file():
                        found.add(str(p.relative_to(root)))
    return found


def _glob_structural_staged():
    """Walk the three structural patterns from the git index."""
    found = set()
    try:
        r = subprocess.run(
            ["git", "ls-files", "--cached", "--",
             "scripts/hooks/*",
             ".github/workflows/*.yml",
             "proofs/*/check_*.py"],
            capture_output=True, text=True, check=True,
        )
        for line in r.stdout.splitlines():
            line = line.strip()
            if line:
                found.add(line)
    except subprocess.CalledProcessError:
        pass
    return found


def _exists_staged(path):
    """Check whether a path exists in the git index."""
    r = subprocess.run(
        ["git", "cat-file", "-e", ":%s" % path],
        capture_output=True,
    )
    return r.returncode == 0


def _index_mode(path):
    """The index mode of a path (`git ls-files --stage`), or None when it is not staged."""
    r = subprocess.run(
        ["git", "ls-files", "--stage", "--", path],
        capture_output=True, text=True,
    )
    parts = r.stdout.split()
    return parts[0] if r.returncode == 0 and parts else None


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(
        description="Advisory-exclusion screen: no Laya/Jev vocabulary in gate files.",
    )
    parser.add_argument(
        "--root", type=str, default=None,
        help="Scan this tree instead of the repo (for fixture trees).",
    )
    parser.add_argument(
        "--list", type=str, default=None,
        help="Path to the allowlist (default: <root>/scripts/gate_files.txt).",
    )
    parser.add_argument(
        "--staged", action="store_true",
        help="Scan staged (index) content via git show instead of files on disk.",
    )
    args = parser.parse_args()

    # Determine root
    if args.root is not None:
        root = Path(args.root).resolve()
    else:
        root = Path.cwd()

    # Determine allowlist path and load entries
    if args.list is not None:
        list_path = Path(args.list)
        if not list_path.exists():
            print("gate-file-missing: %s" % list_path, file=sys.stderr)
            return 64
        entries = _load_allowlist(list_path)
    elif args.staged:
        allowlist_content = _read_staged("scripts/gate_files.txt")
        if allowlist_content is None:
            print("gate-file-missing: scripts/gate_files.txt", file=sys.stderr)
            return 64
        entries = _parse_allowlist(allowlist_content)
    else:
        list_path = root / "scripts" / "gate_files.txt"
        if not list_path.exists():
            print("gate-file-missing: %s" % list_path, file=sys.stderr)
            return 64
        entries = _load_allowlist(list_path)

    # Self-listing check
    for e in entries:
        if e == SELF_PATH:
            print("gate-file-self: %s" % SELF_PATH, file=sys.stderr)
            return 64

    # --- Completeness control ---
    completeness_errors = []
    if args.staged:
        structural_matches = _glob_structural_staged()
    else:
        structural_matches = _glob_structural(root)
    listed_set = set(entries)
    for path in sorted(structural_matches):
        if path not in listed_set:
            completeness_errors.append("gate-file-unlisted: %s" % path)

    # Check listed paths exist AND are regular files (index-backed in staged,
    # lstat-backed otherwise). A symlink is refused by name: reading it would
    # screen its link text (staged) or its target (worktree), not the gate file.
    for entry in entries:
        if args.staged:
            if not _exists_staged(entry):
                completeness_errors.append("gate-file-missing: %s" % entry)
                continue
            mode = _index_mode(entry)
            if mode not in REGULAR_INDEX_MODES:
                completeness_errors.append("gate-file-not-regular: %s mode=%s" % (entry, mode))
        else:
            fp = root / entry
            if fp.is_symlink():
                completeness_errors.append("gate-file-not-regular: %s symlink" % entry)
            elif not fp.exists():
                completeness_errors.append("gate-file-missing: %s" % entry)
            elif not stat.S_ISREG(os.lstat(fp).st_mode):
                completeness_errors.append("gate-file-not-regular: %s not-a-regular-file" % entry)

    if completeness_errors:
        for err in completeness_errors:
            print(err, file=sys.stderr)
        return 4

    contents = {}
    for entry in entries:
        content = _read_staged(entry) if args.staged else _read_file(root, entry)
        if content is None:
            print("gate-file-unreadable: %s" % entry, file=sys.stderr)
            return 4
        contents[entry] = content

    # --- Include edges (AMENDMENT 2): no sourcing; Python imports closed over the list ---
    tree = _Tree(root, args.staged)
    include_errors = []
    for entry in entries:
        if _is_python_gate(entry, contents[entry]):
            include_errors.extend(_import_errors(entry, contents[entry], tree, listed_set))
        else:
            include_errors.extend(_source_errors(entry, contents[entry]))
    if include_errors:
        for err in include_errors:
            print(err, file=sys.stderr)
        return 4

    # --- Scan ---
    violations = []
    scanned = 0
    for entry in entries:
        is_py = entry.endswith(".py")
        content = contents[entry]
        scanned += 1
        for lineno, line in enumerate(content.splitlines(), 1):
            for token in _check_line(line, is_py):
                violations.append("%s:%d:%s" % (entry, lineno, token))

    if violations:
        for v in violations:
            print(v)
        return 3

    print("no_laya_in_gates: %d files scanned, clean" % scanned, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
