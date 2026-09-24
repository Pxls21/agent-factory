#!/usr/bin/env python3
"""search-intercept.py — PreToolUse (Grep|Bash): answer a semantic search once, and stop a known Bash quirk once.

D-072 item 4 (tasks #228, #225). The owner: "when you try to run grep, it blocks you, it runs it itself, and then it
gives you the output, the condensed, serialized output. It prunes it." graft-first-nag.py only nagged, and the nag was
ignored; a rule written in CLAUDE.md does not stop a recurring command shape either. This hook blocks ONCE, explains or
answers, and lets an identical repeat through.

(a) SEARCH. A semantic search is classified by graft-first-nag.py's own classifier (a bare identifier aimed at project
    code), run in-process on the real file, never copied (AF-AP-186). It applies to a Grep call, and to a SIMPLE Bash
    `grep`/`rg` command, optionally piped into head/tail/wc; a compound command is never intercepted for search. The
    search must stay inside this repository (graft indexes nothing else). It is answered here: `graft ask` for the
    identifier in the path, and the search itself (rg with the same pattern, path and glob, capped), in the call's own
    output mode (file names, counts or lines; an output it cannot reproduce, such as context lines or -o, passes
    through) and scope (a Grep call searches what the Grep tool searches; a Bash rg keeps rg's defaults; a Bash grep
    also reads hidden paths, and its answer names what grep -r reads that rg skips) (VERIFY-JT3 F-1, F-2). The hits
    stay in FILE ORDER: the first ones that fit are shown, and the rest are cut, counted per file, and named as what
    the repeat returns. Exit 2, the answer on stderr. A Jev reorder of the SHOWN hits (jev.rank, the local Laya
    server) sits behind a switch that is OFF by default: the file .jev/intercept-jev-rank-on or
    AF_SEARCH_INTERCEPT_JEV_RANK=1
    (coordinator ruling 2026-09-24 13:3xZ: the J2 probe measured Jev's noul reranking picking the right row first 5% of
    the time, below random). No Jev score decides which hits are cut (KC-J5, needle loss).
(b) QUIRK. A Bash command that matches a SHIPPED rule of QUIRK_RULES is blocked with the rule's explanation and its
    CLAUDE.md or AF-AP anchor on stderr, exit 2. The table is closed; a rule ships only when its false-positive rate
    (a block of a command that would have run as intended), read on this session's transcripts, is 5% or less
    (tasks/briefs/jev-laya/JT3-report.md section 2; trailing-amp re-measured in JT3-R1-report.md section 3).
(c) ESCAPE HATCH. The same tool name and input seen again within 120 s passes untouched (exit 0), so a wrong intercept
    costs one call. The Bash `description` field is left out of the key: it is a label, never executed. The record is
    written BEFORE the block, and when it cannot be written the hook does not block. State: .jev/intercept-seen.json
    (0600; entries older than 10 minutes are pruned).

Fail-open: any error, a missing tool (graft, rg), a timeout (graft 20 s, the whole hook 45 s) or a malformed payload
exits 0 with no output. Off switch: the file .jev/intercept-off, or AF_SEARCH_INTERCEPT=0 in the hook's environment.
Every answer stays under 9,000 characters (AF-AP-183: the harness swaps hook text over 10,000 for a 2 KB preview), and
its first line says what happened and how to get the raw result. Standard library only, plus graft and rg on the PATH.

Test seams, read once at start: AF_SEARCH_INTERCEPT_STATE (the state directory instead of <repo>/.jev) and
AF_SEARCH_INTERCEPT_JEV_URL (a loopback Laya endpoint instead of 127.0.0.1:47411).
"""
import json
import os
import re
import signal
import sys
import time

# This hook runs on EVERY Bash call, so the path that decides "nothing to do" stays cheap: the modules only a search or
# a quirk needs (subprocess, select, shutil, hashlib, importlib, contextlib, io, warnings) are imported where they are
# used. Measured 2026-09-24 on a non-matching command: 46.3 ms median with them at the top, 33.5 ms without.

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NAG = os.path.join(ROOT, ".claude", "hooks", "graft-first-nag.py")

WINDOW_S = 120            # D-1 (c): an identical repeat within this window passes untouched
PRUNE_S = 600             # seen entries older than 10 minutes are dropped
GRAFT_TIMEOUT_S = 20      # D-3
HOOK_BUDGET_S = 45        # D-3: the whole hook (hook_context.py allows 55 s, Claude Code 60 s)
RG_TIMEOUT_S = 10
RG_MAX_BYTES = 2_000_000  # rg's output is read up to this many bytes, then rg is stopped
RANK_ABOVE = 12           # the Jev switch (off by default) reorders the shown hits only when there are more than 12
RANK_TIMEOUT_S = 20       # jev.rank takes about 0.45 s per hit on the local CPU server (JT1's A1)
SHOW = 20                 # at most this many hits shown, a prefix of file order; the rest are cut and counted per file
MAX_ANSWER = 8_800        # D-4: every answer under 9,000 characters
CUT_RESERVE = 1_300       # room kept for the "Cut:" line
GRAFT_CHARS = 2_600
LINE_CHARS = 220
MAX_CMD = 200_000         # a longer Bash command is not analysed
FIRST_LINE = "repeat the identical call within 120 s for the raw result"

_children = []


# ---------------------------------------------------------------- a small shell lexer (quotes, substitutions, heredocs)

class Unparsed(ValueError):
    """A command this lexer cannot read (an unbalanced quote or substitution): nothing is decided on it."""


class Word:
    """One shell word: its raw text, its value with quotes removed, whether it holds a substitution or a variable
    (`subst`), whether it holds an unescaped backtick inside double quotes (`dq_tick`), and the names of the parameters
    it expands outside single quotes (`refs`: `$!` gives "!", `${SP:-x}` gives "SP")."""
    __slots__ = ("raw", "value", "subst", "dq_tick", "refs")

    def __init__(self, raw="", value=""):
        self.raw, self.value, self.subst, self.dq_tick, self.refs = raw, value, False, False, []


_OPS = ("&>>", "<<-", "<<<", "&&", "||", ";;", "|&", ">>", "<<", "<&", ">&", "&>", "<>", ">|",
        ";", "&", "|", "(", ")", "<", ">")
_META = frozenset(";&|()<> \t\n")
_REDIR = frozenset({"<", ">", ">>", ">|", "<<", "<<-", "<<<", "<&", ">&", "&>", "&>>", "<>"})
_VAR = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[0-9@*#?$!-]")
_RESERVED = frozenset({"{", "}", "!", "if", "then", "else", "elif", "do", "while", "until", "time"})


def _op_at(s, i):
    for op in _OPS:
        if s.startswith(op, i):
            return op
    return None


def _backtick_end(s, i):
    n = len(s)
    while i < n:
        if s[i] == "\\":
            i += 2
        elif s[i] == "`":
            return i
        else:
            i += 1
    raise Unparsed("unterminated backtick")


def _heredoc_skip(s, i, delim, strip):
    """The index after the line that closes a here-document body that starts at i."""
    n = len(s)
    while i < n:
        j = s.find("\n", i)
        line, nxt = (s[i:], n) if j < 0 else (s[i:j], j + 1)
        if (line.lstrip("\t") if strip else line) == delim:
            return nxt
        i = nxt
    return n


def _heredoc_delim(s, i):
    """(delimiter, strip_tabs, index after it) for the `<<` or `<<-` at s[i]."""
    i += 2
    strip = s.startswith("-", i)
    i += 1 if strip else 0
    while i < len(s) and s[i] in " \t":
        i += 1
    w, i = _read_word(s, i, [])
    return w.value, strip, i


def _dq_end(s, i):
    """The index after the double quote that closes a string whose body starts at i."""
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2
        elif c == '"':
            return i + 1
        elif c == "`":
            i = _backtick_end(s, i + 1) + 1
        elif s.startswith("$(", i):
            i = _group_end(s, i + 2, "(", ")") + 1
        elif s.startswith("${", i):
            i = _group_end(s, i + 2, "{", "}") + 1
        else:
            i += 1
    raise Unparsed("unterminated double quote")


def _group_end(s, i, open_ch, close_ch):
    """The index of the `close_ch` that closes a group whose opener sits just before s[i] (a `$(...)` body may hold
    quotes, nested groups and here-documents)."""
    n, depth, pending = len(s), 1, []
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2
        elif c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise Unparsed("unterminated quote")
            i = j + 1
        elif c == '"':
            i = _dq_end(s, i + 1)
        elif c == "`":
            i = _backtick_end(s, i + 1) + 1
        elif c == "\n" and pending:
            i += 1
            for d, st in pending:
                i = _heredoc_skip(s, i, d, st)
            pending = []
        elif open_ch == "(" and s.startswith("<<", i) and not s.startswith("<<<", i):
            d, st, i = _heredoc_delim(s, i)
            pending.append((d, st))
        else:
            if c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return i
            i += 1
    raise Unparsed("unterminated group")


def _read_dollar(s, i, val, w, subs):
    nxt = s[i + 1:i + 2]
    if nxt == "(":
        j = _group_end(s, i + 2, "(", ")")
        subs.append(s[i + 2:j])
        val.append(s[i:j + 1])
        w.subst = True
        return j + 1
    if nxt == "{":
        j = _group_end(s, i + 2, "{", "}")
        m = _VAR.match(s, i + 2)
        if m:
            w.refs.append(m.group(0))
        val.append(s[i:j + 1])
        w.subst = True
        return j + 1
    if nxt == "'":                      # $'...' (ANSI-C quoting): kept undecoded, never a substitution
        j, n = i + 2, len(s)
        while j < n and s[j] != "'":
            j += 2 if s[j] == "\\" else 1
        if j >= n:
            raise Unparsed("unterminated $'")
        val.append(s[i + 2:j])
        return j + 1
    m = _VAR.match(s, i + 1)
    if m:
        w.refs.append(m.group(0))
        val.append(s[i:m.end()])
        w.subst = True
        return m.end()
    val.append("$")
    return i + 1


def _read_dq(s, i, val, w, subs):
    n = len(s)
    while i < n:
        c = s[i]
        if c == '"':
            return i + 1
        if c == "\\":
            nxt = s[i + 1:i + 2]
            if nxt in ('"', "\\", "$", "`"):
                val.append(nxt)
                i += 2
            elif nxt == "\n":
                i += 2
            else:
                val.append("\\")
                i += 1
        elif c == "`":
            j = _backtick_end(s, i + 1)
            subs.append(s[i + 1:j])
            val.append(s[i:j + 1])
            w.subst = w.dq_tick = True
            i = j + 1
        elif c == "$":
            i = _read_dollar(s, i, val, w, subs)
        else:
            val.append(c)
            i += 1
    raise Unparsed("unterminated double quote")


def _read_word(s, i, subs):
    w, val, n, start = Word(), [], len(s), i
    while i < n:
        c = s[i]
        if c in _META:
            break
        if c == "\\":
            if not s.startswith("\n", i + 1):
                val.append(s[i + 1:i + 2])
            i += 2
        elif c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise Unparsed("unterminated quote")
            val.append(s[i + 1:j])
            i = j + 1
        elif c == '"':
            i = _read_dq(s, i + 1, val, w, subs)
        elif c == "`":
            j = _backtick_end(s, i + 1)
            subs.append(s[i + 1:j])
            val.append(s[i:j + 1])
            w.subst = True
            i = j + 1
        elif c == "$":
            i = _read_dollar(s, i, val, w, subs)
        else:
            val.append(c)
            i += 1
    w.raw, w.value = s[start:i], "".join(val)
    return w, i


def lex(s):
    """(tokens, substitution bodies). A token is ("w", Word) or ("op", text). Comments and here-document bodies are
    dropped; an IO number joins its redirection (`2>`); a newline is the operator "\\n". Raises Unparsed."""
    toks, subs, pending, i, n = [], [], [], 0, len(s)
    while i < n:
        c = s[i]
        if c in " \t":
            i += 1
        elif c == "\\" and s.startswith("\n", i + 1):
            i += 2
        elif c == "\n":
            toks.append(("op", "\n"))
            i += 1
            for d, st in pending:
                i = _heredoc_skip(s, i, d, st)
            pending = []
        elif c == "#":
            j = s.find("\n", i)
            i = n if j < 0 else j
        else:
            op = _op_at(s, i)
            if op in ("<<", "<<-"):
                d, st, i = _heredoc_delim(s, i)
                pending.append((d, st))
                toks += [("op", op), ("w", Word(d, d))]
            elif op:
                toks.append(("op", op))
                i += len(op)
            else:
                w, i = _read_word(s, i, subs)
                if w.raw.isdigit() and i < n and s[i] in "<>":
                    op = _op_at(s, i)
                    toks.append(("op", w.raw + op))
                    i += len(op)
                else:
                    toks.append(("w", w))
    return toks, subs


def _mid_cap(text, limit):
    """Text cut in the middle to at most `limit` characters: a quirk usually sits at the end."""
    return text if len(text) <= limit else text[:limit // 3] + " … " + text[-(limit - limit // 3 - 3):]


def _is_redir(op):
    return op in _REDIR or op[:1].isdigit()


def simple_commands(toks, strip=True):
    """Each simple command's words, redirections and their targets dropped; with `strip`, leading reserved words and
    VAR=value assignments stripped too."""
    cmds, cur, skip = [], [], False
    for kind, v in toks:
        if kind == "op":
            if _is_redir(v):
                skip = True
            elif cur:
                cmds.append(cur)
                cur = []
            continue
        if skip:
            skip = False
        elif not strip or cur or v.raw not in _RESERVED:
            if not strip or cur or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", v.raw, re.S):
                cur.append(v)
    if cur:
        cmds.append(cur)
    return cmds


class Parsed:
    """A command lexed once: the top level and every substitution body, each with its tokens and simple commands."""

    def __init__(self, text):
        self.text = text
        self.levels = []            # [(tokens, simple commands)], the top level first
        self.top_ops = []
        todo, seen = [text], 0
        while todo and seen < 64:
            toks, subs = lex(todo.pop(0))
            seen += 1
            self.levels.append((toks, simple_commands(toks)))
            todo += subs
        self.top_ops = [v for k, v in self.levels[0][0] if k == "op"]
        self.has_subst = len(self.levels) > 1 or any(k == "w" and v.subst for k, v in self.levels[0][0])

    def commands(self):
        for _, cmds in self.levels:
            yield from cmds


# ---------------------------------------------------------------- (b) the quirk table

_ASSIGN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=")
_NAME_ARG = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)(?:=|$)")
_DECLARE = frozenset({"export", "declare", "typeset", "readonly", "local"})


def _amp_harm(lst, rest):
    """What a later step loses when the whole list `lst` runs in one background subshell, read from the tokens `rest`
    after its `&`: `$!` read before any other `&` (it names the subshell, not the job), or a variable the list assigns
    read at all (the assignment ran in the subshell). None when neither is read."""
    assigned = set()
    for words in simple_commands(lst, strip=False):
        if all(_ASSIGN.match(w.raw) for w in words):
            assigned.update(_ASSIGN.match(w.raw).group(1) for w in words)
        elif words[0].value in _DECLARE:
            assigned.update(m.group(1) for m in (_NAME_ARG.match(w.value) for w in words[1:]) if m)
    bang = True
    for kind, v in rest:
        if kind == "op":
            bang = bang and v != "&"            # after another `&`, `$!` names that later job
            continue
        if bang and "!" in v.refs:
            return "`$!` is read after it (the subshell's pid, not the job's)"
        used = sorted(assigned.intersection(v.refs))
        if used:
            return "`$%s` is read after it (the list assigned it inside the subshell)" % used[0]
    return None


def _closes_group(toks, k):
    """True when the next token from index k on, newlines skipped, is a `)`."""
    while k < len(toks) and toks[k] == ("op", "\n"):
        k += 1
    return k < len(toks) and toks[k] == ("op", ")")


def _shown(toks):
    return " ".join(v.raw if kind == "w" else (";" if v == "\n" else v) for kind, v in toks)


def _rule_trailing_amp(p):
    """A `&&` list ended by `&`: the WHOLE list runs in one background subshell. It is blocked only when that changes
    the outcome: a later step reads `$!` or a variable the list assigns (_amp_harm). Never blocked: a list grouped on
    purpose, `( ... ) &` or `{ ...; } &` (its `&&` sits one level down), and the detach form `( ... && job & )`, whose
    `&` closes its own subshell, so nothing after the group can see the list (VERIFY-JT3 F-3: 25 of 25 such launches
    in this session ran as intended). Returns the list and the harm as found."""
    for toks, _ in p.levels:
        stack, starts, first = [[False, None]], [0], True     # per group: [inside a && list, "(" or "{"]
        for k, (kind, v) in enumerate(toks):
            if kind == "w":
                if first and v.raw == "{":
                    stack.append([False, "{"])
                    starts.append(k + 1)
                    continue
                if first and v.raw == "}" and len(stack) > 1:
                    stack.pop()
                    starts.pop()
                first = False
                continue
            if _is_redir(v):
                continue
            if v == "(":
                stack.append([False, "("])
                starts.append(k + 1)
                first = True
            elif v == ")":
                if len(stack) > 1:
                    stack.pop()
                    starts.pop()
                first = False
            elif v == "&&":
                stack[-1][0], first = True, True
            elif v == "&":
                if stack[-1][0] and not (stack[-1][1] == "(" and _closes_group(toks, k + 1)):
                    harm = _amp_harm(toks[starts[-1]:k], toks[k + 1:])
                    if harm:
                        return "the list `%s`, and %s" % (_mid_cap(_shown(toks[starts[-1]:k + 1]), 240), harm)
                stack[-1][0], first, starts[-1] = False, True, k + 1
            elif v in (";", ";;", "\n"):
                stack[-1][0], first, starts[-1] = False, True, k + 1
            else:
                first = True
    return None


_PKILL_VALUE_SHORT = set("gGPstuUOrF")
_SIGNAL = re.compile(r"[0-9]+|(?:SIG)?[A-Z][A-Z0-9+-]+")    # -9, -KILL, -SIGTERM; a single capital is an option (-A)
_PKILL_VALUE_LONG = {"signal", "pgroup", "group", "parent", "session", "terminal", "euid", "uid", "older", "ns",
                     "nslist", "runstates", "cgroup", "env", "pidfile", "delimiter"}


def _pkill_args(words):
    """(full, exact, icase, inverse_or_ancestors, pattern word) for pkill's arguments."""
    full = exact = icase = skip_all = False
    pat, k, rest_positional = None, 0, False
    while k < len(words):
        w = words[k]
        v = w.value
        k += 1
        if not rest_positional and v == "--":
            rest_positional = True
            continue
        if not rest_positional and v.startswith("--") and len(v) > 2:
            name, eq, _ = v[2:].partition("=")
            full |= name == "full"
            exact |= name == "exact"
            icase |= name == "ignore-case"
            skip_all |= name in ("inverse", "ignore-ancestors")
            if name in _PKILL_VALUE_LONG and not eq:
                k += 1
            continue
        if not rest_positional and v.startswith("-") and len(v) > 1:
            body = v[1:]
            if _SIGNAL.fullmatch(body):
                continue
            for j, ch in enumerate(body):
                full |= ch == "f"
                exact |= ch == "x"
                icase |= ch == "i"
                skip_all |= ch in "vA"
                if ch in _PKILL_VALUE_SHORT:
                    k += 0 if body[j + 1:] else 1
                    break
            continue
        pat = w
    return full, exact, icase, skip_all, pat


def _rule_pkill_self(p):
    """`pkill -f PAT` where PAT matches the command's own text: the Bash tool runs every command through `eval` inside
    `bash -c '... && eval '<command>' && ...'`, so that shell's command line holds the text and pkill kills it."""
    import warnings
    texts = (p.text, p.text.replace("'", "'\"'\"'"))
    for words in p.commands():
        if os.path.basename(words[0].value) != "pkill":
            continue
        full, exact, icase, skip_all, pat = _pkill_args(words[1:])
        if not full or exact or skip_all or pat is None or not pat.value:
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                rx = re.compile(pat.value, re.I if icase else 0)
        except (re.error, OverflowError, RecursionError):
            continue
        for t in texts:
            m = rx.search(t)
            if m:
                return "`pkill -f %s` matches its own shell's command line (%r)" % (pat.raw[:80], m.group(0)[:60])
    return None


def _rule_safe_commit_tick(p):
    """Backticks inside a double-quoted `safe_commit.sh -m "..."` message: bash runs them as command substitutions."""
    for words in p.commands():
        for k, w in enumerate(words):
            if os.path.basename(w.value) == "safe_commit.sh":
                rest = words[k + 1:]
                if len(rest) >= 2 and rest[0].value == "-m" and rest[1].dq_tick:
                    return "a backtick inside the double-quoted `safe_commit.sh -m` message"
                break
    return None


_GIT_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def _rule_rev_parse_two(p):
    """`git rev-parse --short` with two or more revisions: git refuses (fatal: Needed a single revision, rc 128)."""
    for words in p.commands():
        vals = [w.value for w in words]
        if os.path.basename(vals[0]) != "git":
            continue
        j = 1
        while j < len(vals) and vals[j].startswith("-"):
            j += 2 if vals[j] in _GIT_VALUE_OPTS else 1
        if j >= len(vals) or vals[j] != "rev-parse":
            continue
        args = vals[j + 1:]
        if "--" in args:
            args = args[:args.index("--")]
        short = any(a == "--short" or a.startswith("--short=") for a in args)
        revs = [a for a in args if not a.startswith("-")]
        if short and len(revs) >= 2:
            return "`git rev-parse --short` with %d revisions" % len(revs)
    return None


QUIRK_RULES = {
    "trailing-amp": (_rule_trailing_amp, (
        "A `&&` list ends in a trailing `&`, so the WHOLE list runs in one background subshell, and a later step reads "
        "what that subshell took with it: `$!` is the subshell's pid, not your job's (`kill $!` leaves the job "
        "running), and a variable the list assigns is unset after it.",
        'CLAUDE.md "A trailing `&` backgrounds the WHOLE `&&` list" (bit 2026-09-21 and 2026-09-24 12:1xZ; task #225).',
        "End the list before the job: `a && b` on one line, then `nohup c > log 2>&1 &` on its own line, so `$!` is "
        "the job's pid and the list's variables stay in your shell.")),
    "pkill-self": (_rule_pkill_self, (
        "The pattern matches this command's own text, and the Bash tool runs every command through `eval` inside "
        "`bash -c '... eval '<command>' ...'`: pkill matches that shell and kills it (rc 143 or 144; the rest never "
        "runs).",
        'CLAUDE.md "kill by pid, never by `pkill -f` inside a compound command that also names the target" '
        "(rc 144, 2026-09-14; AF-AP-34).",
        "Kill by pid: read a pidfile, or run `pgrep -f '[x]yz'` in its OWN call, then `kill <pid>`.")),
    "safe-commit-backtick": (_rule_safe_commit_tick, (
        "Inside double quotes bash runs each `...` span as a command substitution, so the phrase vanishes from the "
        "commit message (or runs as a command).",
        'CLAUDE.md "`scripts/safe_commit.sh -m "…"`: no backticks inside a double-quoted message" (2026-09-15).',
        "Single-quote the message, escape each backtick as \\`, or write the message to a file.")),
    "rev-parse-two": (_rule_rev_parse_two, (
        "`git rev-parse --short` takes ONE revision; with two it fails: fatal: Needed a single revision (rc 128).",
        'CLAUDE.md "`git rev-parse --short REV1 REV2` fails ... one rev-parse per call".',
        "Run one `git rev-parse --short <rev>` per revision.")),
}
# The measured table. A false positive is a block of a command that would have run as intended (VERIFY-JT3 F-3).
# trailing-amp, narrowed after F-3 and re-measured on the main and the subagent transcripts (32,729 Bash commands):
# 1 false positive in 53 fires, every one read (1.9%; JT3-R1-report.md section 3). pkill-self 1 in 35 known outcomes
# (VERIFY-JT3 3.3); safe-commit-backtick 2 of 2 and rev-parse-two 4 of 4 real. A rule outside SHIPPED never fires.
SHIPPED = ("trailing-amp", "pkill-self", "safe-commit-backtick", "rev-parse-two")


def quirk(p, rules=None):
    """(rule id, detail) of the first shipped rule the parsed command matches, else None."""
    for rid in (SHIPPED if rules is None else rules):
        detail = QUIRK_RULES[rid][0](p)
        if detail:
            return rid, detail
    return None


def quirk_message(rid, detail):
    why, anchor, fix = QUIRK_RULES[rid][1]
    return "\n".join((
        "QUIRK GUARD (search-intercept.py, rule %s): this Bash command was NOT run; %s." % (rid, FIRST_LINE),
        "Found: %s." % detail, why, "Anchor: " + anchor, "Fix: " + fix))


# ---------------------------------------------------------------- (a) the search: classify, run, answer

# Options a search may carry. Anything else, and an output this hook does not reproduce (context lines, -o, grep -a,
# rg --count-matches), is refused: the call passes through (VERIFY-JT3 F-2). -l and -c set the answer's mode.
_GREP_FLAGS = set("rRnHhiwFEsIlcP")
_GREP_VALUE = set("em")
_GREP_LONG = {"recursive": "r", "dereference-recursive": "R", "line-number": "", "with-filename": "", "no-filename": "",
              "ignore-case": "i", "word-regexp": "w", "fixed-strings": "F", "extended-regexp": "E",
              "perl-regexp": "E", "no-messages": "", "files-with-matches": "l", "count": "c", "null": "",
              "initial-tab": "", "color": "", "colour": ""}
_GREP_LONG_VALUE = {"include", "exclude", "exclude-dir", "max-count", "regexp"}
_RG_FLAGS = set("nNiswSFHIlcup.PU")
_RG_VALUE = set("etTgmMj")
_RG_LONG = {"line-number": "", "no-line-number": "", "ignore-case": "i", "case-sensitive": "", "smart-case": "S",
            "word-regexp": "w", "fixed-strings": "F", "with-filename": "", "no-filename": "",
            "files-with-matches": "l", "count": "c", "no-heading": "", "heading": "", "hidden": ".", "no-ignore": "u",
            "no-ignore-vcs": "V", "pcre2": "", "multiline": "", "no-messages": "", "column": "", "no-column": "",
            "trim": "", "color": "", "colour": "", "follow": "L"}
_RG_LONG_VALUE = {"type", "type-not", "glob", "iglob", "max-count", "max-columns", "sort", "sortr", "threads",
                  "max-depth", "regexp"}


def _parse_search(prog, args):
    """A search spec from a grep or rg argument list, or None when an option is not one this hook reproduces."""
    grep = prog in ("grep", "egrep", "fgrep")
    flags, value_short, long_flags, long_value = (
        (_GREP_FLAGS, _GREP_VALUE, _GREP_LONG, _GREP_LONG_VALUE) if grep else
        (_RG_FLAGS, _RG_VALUE, _RG_LONG, _RG_LONG_VALUE))
    spec = {"prog": "grep" if grep else "rg", "pattern": None, "paths": [], "globs": [], "type": "", "i": False,
            "w": False, "F": prog == "fgrep", "E": prog == "egrep", "r": not grep, "extra": [], "mode": "content"}
    positional, k, modes = [], 0, set()

    def setflag(ch):
        if ch in "iwFE":
            spec[ch] = True
        elif ch in "rR":
            spec["r"] = True if grep else spec["r"]
            if grep and ch == "R":
                spec["extra"].append("--follow")        # grep -R follows symbolic links; -r does not
        elif ch in "lc":
            modes.add(ch)
        elif ch == "P":
            spec["E"] = True
        elif not grep and ch in "S.uLV":
            spec["extra"].append({"S": "--smart-case", ".": "--hidden", "u": "-u", "L": "--follow",
                                  "V": "--no-ignore-vcs"}[ch])

    def setvalue(opt, val):
        if opt in ("e", "regexp"):
            if spec["pattern"] is not None:
                return False
            spec["pattern"] = val
        elif opt in ("t", "type"):
            spec["type"] = val
        elif opt in ("g", "glob", "include"):
            spec["globs"].append(val)
        elif opt in ("exclude", "exclude-dir"):
            spec["globs"].append("!" + val)
        elif opt in ("T", "type-not"):
            spec["extra"] += ["--type-not", val]
        elif opt == "iglob":
            spec["extra"] += ["--iglob", val]
        elif opt == "max-depth":
            spec["extra"] += ["--max-depth", val]
        elif opt in ("m", "max-count"):
            spec["extra"] += ["--max-count", val]         # per file, in grep and in rg
        return True

    while k < len(args):
        a = args[k].value
        k += 1
        if a == "--":
            positional += [w.value for w in args[k:]]
            break
        if a.startswith("--") and len(a) > 2:
            name, eq, val = a[2:].partition("=")
            if name in long_value:
                if not eq:
                    if k >= len(args):
                        return None
                    val, k = args[k].value, k + 1
                if not setvalue(name, val):
                    return None
            elif name in long_flags:
                setflag(long_flags[name])
            else:
                return None
            continue
        if a.startswith("-") and len(a) > 1:
            body = a[1:]
            for j, ch in enumerate(body):
                if ch in value_short:
                    val = body[j + 1:]
                    if not val:
                        if k >= len(args):
                            return None
                        val, k = args[k].value, k + 1
                    if not setvalue(ch, val):
                        return None
                    break
                if ch not in flags:
                    return None
                setflag(ch)
            continue
        positional.append(a)
    if spec["pattern"] is None:
        if not positional:
            return None
        spec["pattern"] = positional.pop(0)
    if len(modes) > 1:
        return None                                     # -l with -c: not guessed
    spec["paths"] = positional
    spec["mode"] = {"l": "names", "c": "count"}[modes.pop()] if modes else "content"
    return spec


def bash_search(p):
    """The search spec of a SIMPLE grep/rg command, optionally piped into head/tail/wc (a stderr redirection to
    /dev/null or to stdout allowed), else None. A compound command, a variable or a substitution is never a search."""
    toks = list(p.levels[0][0])
    while toks and toks[-1] == ("op", "\n"):
        toks.pop()
    if len(p.levels) > 1 or not toks:
        return None
    segs, cur, k = [[]], None, 0
    cur = segs[0]
    while k < len(toks):
        kind, v = toks[k]
        k += 1
        if kind == "w":
            if v.subst:
                return None
            cur.append(v)
        elif v == "|":
            cur = []
            segs.append(cur)
        elif v in ("2>", "2>>") and k < len(toks) and toks[k][0] == "w" and toks[k][1].value == "/dev/null":
            k += 1
        elif v == "2>&" and k < len(toks) and toks[k][0] == "w" and toks[k][1].value == "1":
            k += 1
        else:
            return None
    if any(not s for s in segs):
        return None
    if any(os.path.basename(s[0].value) not in ("head", "tail", "wc") for s in segs[1:]):
        return None
    prog = os.path.basename(segs[0][0].value)
    if prog not in ("grep", "egrep", "fgrep", "rg"):
        return None
    return _parse_search(prog, segs[0][1:])


_GREP_TOOL_MODES = {None: "names", "files_with_matches": "names", "count": "count", "content": "content"}
_GREP_TOOL_CONTENT_ONLY = ("-A", "-B", "-C", "context", "-o")    # the Grep tool reads these in content mode only


def grep_tool_splits(glob):
    """True when the Grep tool reads `glob` as SEVERAL globs, while rg reads one (VERIFY-JT3-R1 N-1: `*.sh,*.md` was
    answered "0 hits"). The tool splits on whitespace ANYWHERE, U+FEFF included (JS `\\s`), before it looks at braces,
    and on commas outside braces (VERIFY-JT3-R1 R2-1, R2-2). Unbalanced braces count too: never guess."""
    depth = 0
    for ch in glob:
        if ch.isspace() or ch == chr(0xFEFF):
            return True
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth == 0:
                return True
            depth -= 1
        elif depth == 0 and ch == ",":
            return True
    return depth != 0


def grep_tool_search(ti):
    """The search spec of a Grep tool call in its own output mode (file names by default), or None when its output is
    one this hook does not reproduce: context lines, -o, multiline, an offset or a head_limit (VERIFY-JT3 F-2), or a
    glob the tool splits into several (VERIFY-JT3-R1 N-1)."""
    pattern = ti.get("pattern")
    if not isinstance(pattern, str) or not pattern:
        return None
    path, glob, ftype = ti.get("path") or "", ti.get("glob") or "", ti.get("type") or ""
    if not all(isinstance(x, str) for x in (path, glob, ftype)) or grep_tool_splits(glob):
        return None
    om = ti.get("output_mode")
    mode = _GREP_TOOL_MODES.get(om) if om is None or isinstance(om, str) else None
    if (mode is None or ti.get("multiline") or ti.get("offset") or ti.get("head_limit")
            or mode == "content" and any(ti.get(k) for k in _GREP_TOOL_CONTENT_ONLY)):
        return None
    return {"prog": "Grep", "pattern": pattern, "paths": [path] if path else [], "globs": [glob] if glob else [],
            "type": ftype, "i": ti.get("-i") is True, "w": False, "F": False, "E": True, "r": True, "extra": [],
            "mode": mode}


def nag_says_semantic(tool_input):
    """graft-first-nag.py's own verdict on a Grep-shaped input: True when it would nag. The nag's main() runs in-process
    on the real file (never a copy of its classifier, AF-AP-186)."""
    import contextlib
    import importlib.util
    import io
    spec = importlib.util.spec_from_file_location("graft_first_nag", NAG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out, old = io.StringIO(), sys.stdin
    sys.stdin = io.StringIO(json.dumps({"tool_name": "Grep", "tool_input": tool_input}))
    try:
        with contextlib.redirect_stdout(out):
            mod.main()
    finally:
        sys.stdin = old
    return bool(out.getvalue().strip())


def _inside(path, root):
    try:
        return os.path.commonpath([os.path.realpath(path), os.path.realpath(root)]) == os.path.realpath(root)
    except ValueError:
        return False


def semantic_scope(spec, cwd):
    """(search cwd, absolute search roots) when the spec is a semantic search inside this repo, else None."""
    if spec is None:
        return None
    pat = spec["pattern"]
    if spec["prog"] == "grep":
        if not spec["E"] and not spec["F"] and "|" in pat:
            return None                 # a basic-regex `|` is a literal character, not the Grep tool's alternation
        if not spec["r"] and (not spec["paths"] or
                              not all(os.path.isfile(os.path.join(cwd, x)) for x in spec["paths"])):
            return None                 # without -r grep reads stdin, or refuses a directory
    glob = next((g for g in spec["globs"] if not g.startswith("!")), "")
    for path in spec["paths"] or [""]:
        if not nag_says_semantic({"pattern": pat, "path": path, "glob": glob, "type": spec["type"]}):
            return None
    roots = [os.path.normpath(os.path.join(cwd, x)) for x in spec["paths"]] or [cwd]
    if not all(_inside(r, ROOT) for r in roots):
        return None
    return cwd, roots


def _kill(proc, reap=True):
    """Kill the child's whole process group and reap it (no zombie is left behind). The alarm handler passes
    reap=False: waiting inside a signal handler could contend for the Popen lock the main thread holds."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except OSError:
        pass
    if reap:
        try:
            proc.wait(timeout=2)
        except Exception:
            pass


def _spawn(cmd, cwd):
    import subprocess
    proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    _children.append(proc)
    return proc


# What the Grep tool searches, probed on a scratch repo, never assumed (JT3-R1-report.md section 2.1): hidden paths
# yes, these six VCS directories no, ignore files (.gitignore, .ignore) honoured, binary files skipped.
_GREP_TOOL_SCOPE = ["--hidden"] + [a for d in (".git", ".svn", ".hg", ".bzr", ".jj", ".sl")
                                   for a in ("--glob", "!" + d)]
_RG_MODE = {"names": ["--files-with-matches"], "count": ["--count", "--with-filename"],
            "content": ["--line-number", "--no-heading", "--with-filename", "--max-columns", "240",
                        "--max-columns-preview"]}
_BINARY = re.compile(r"(.+): (binary file matches \(.*\))$")     # rg's note for a binary file named as a path


def run_rg(rg, spec, cwd, roots, deadline, timeout=None, max_bytes=None):
    """(hits, cut) from rg with the spec's pattern, paths, globs, scope and output mode. A hit is (path, line, text) for
    a matched line, (path, 0, rg's note) for a binary file named on the command line, (path, count, "") in count mode
    and (path, 0, "") in names mode. The scope (VERIFY-JT3 F-1): a Grep call searches what the Grep tool searches, a
    Bash grep adds hidden paths (grep -r reads them; what rg still skips is named in the answer) and a Bash rg keeps
    rg's own defaults. Raises on an rg error or a timeout (the caller fails open). The limits are read at call time."""
    import select
    timeout = RG_TIMEOUT_S if timeout is None else timeout
    max_bytes = RG_MAX_BYTES if max_bytes is None else max_bytes
    mode = spec["mode"]
    # --sort path: rg's default parallel walk prints files in completion order, so "file order" (and with it the shown
    # prefix and the cut) changed between two identical runs (this lane's first test run); sorted, it is stable.
    cmd = [rg, "--null", "--color", "never", "--sort", "path"] + _RG_MODE[mode]
    cmd += _GREP_TOOL_SCOPE if spec["prog"] == "Grep" else ["--hidden"] if spec["prog"] == "grep" else []
    cmd += ["-i"] if spec["i"] else []
    cmd += ["-w"] if spec["w"] else []
    cmd += ["-F"] if spec["F"] else []
    for g in spec["globs"]:
        cmd += ["--glob", g]
    cmd += ["--type", spec["type"]] if spec["type"] else []
    # No path: pass "." explicitly. rg searches STDIN instead of the cwd when stdin looks readable (a bare `rg -e self`
    # hung on this lane's own Bash stdin); a heuristic change there would turn this answer into a silent "0 hits".
    cmd += spec["extra"] + ["-e", spec["pattern"], "--"] + (list(spec["paths"]) or ["."])
    proc = _spawn(cmd, cwd)
    end = min(deadline, time.monotonic() + timeout)
    buf, cut, fd = bytearray(), False, proc.stdout.fileno()
    while True:
        left = end - time.monotonic()
        if left <= 0:
            _kill(proc)
            raise TimeoutError("rg timed out")
        ready, _, _ = select.select([fd], [], [], left)
        if not ready:
            continue
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        buf += chunk
        if len(buf) > max_bytes:
            cut = True
            _kill(proc)
            break
    rc = proc.wait(timeout=max(0.5, end - time.monotonic()))
    if not cut and rc not in (0, 1):
        raise RuntimeError("rg exited %s" % rc)
    raw = bytes(buf)
    if cut:
        raw = raw[:raw.rfind(b"\0" if mode == "names" else b"\n") + 1]     # names mode has no newline, only NULs
    out = raw.decode("utf-8", "replace")
    if mode == "names":
        return [(p, 0, "") for p in out.split("\0") if p], cut
    hits = []
    for line in out.split("\n"):     # rg ends lines with \n only: never
        # str.splitlines(), which also splits on \x0c, \x85 and U+2028 inside a matched line (AF-AP-132)
        path, sep, rest = line.partition("\0")
        if mode == "count":
            if sep and rest.isdigit():
                hits.append((path, int(rest), ""))
            continue
        num, sep2, text = rest.partition(":")
        m = None if sep else _BINARY.match(line)
        if sep and sep2 and num.isdigit():
            hits.append((path, int(num), text))
        elif m:
            hits.append((m.group(1), 0, m.group(2)))
    return hits, cut


def graft_answer(proc, deadline, timeout=None):
    """graft's answer text (its `[graft]` meta lines and blank lines dropped). Raises on a graft error or a timeout."""
    import subprocess
    timeout = GRAFT_TIMEOUT_S if timeout is None else timeout
    try:
        out, _ = proc.communicate(timeout=max(0.1, min(timeout, deadline - time.monotonic())))
    except subprocess.TimeoutExpired:
        _kill(proc)
        raise
    if proc.returncode != 0:
        raise RuntimeError("graft exited %s" % proc.returncode)
    lines = [ln.rstrip() for ln in out.decode("utf-8", "replace").split("\n")]
    return "\n".join(ln for ln in lines if ln.strip() and not ln.startswith("[graft]"))


def jev_reorder(shown, pattern, deadline, jev_url, state_dir, rank=None):
    """(display order of the SHOWN hits, note); runs only with the Jev switch on. Jev may reorder the hits file order
    already chose; it never sees the cut ones, so no Jev score decides what is dropped (KC-J5, needle loss). Any
    failure keeps file order (D-1)."""
    order = list(range(len(shown)))
    t = min(RANK_TIMEOUT_S, deadline - time.monotonic() - 3)
    if t < 2:
        return order, "no time was left for the Jev reorder"
    reason = "no answer"
    try:
        if rank is None:
            sys.path.insert(0, os.path.join(ROOT, "scripts"))
            import jev
            rank = jev.rank
        chunks = [{"id": "h%d" % i, "text": "%s:%d: %s" % (h[0], h[1], h[2].strip())} for i, h in enumerate(shown)]
        t0 = time.monotonic()
        res = rank("Where is %s defined, and which lines show how it is used?" % pattern, chunks, venue="local",
                   url=jev_url, timeout=t, log_path=os.path.join(state_dir, "calls.jsonl"))
        took = time.monotonic() - t0
        ranked = [int(r[0][1:]) for r in (res or {}).get("ranking") or []]
        if sorted(ranked) == order:
            return ranked, "reordered by Jev (advisory, a switch that is off by default; %.1f s)" % took
        reason = (getattr(sys.modules.get("jev"), "last_reason", None) or reason) if res is None else "a bad ranking"
    except Exception as e:                  # fail open to file order (D-1)
        reason = type(e).__name__
    return order, "the Jev reorder was unavailable (%s)" % " ".join(str(reason).split())[:120]


def _cap(text, limit):
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _hit_line(h, mode="content"):
    """One shown entry: a file name (names mode), `path:count` (count mode), `path:line: text`, or rg's note for a
    binary file named on the command line (content mode, line 0)."""
    if mode == "names":
        return _cap(h[0], LINE_CHARS)
    if mode == "count":
        return _cap("%s:%d" % (h[0], h[1]), LINE_CHARS)
    if h[1] == 0:
        return _cap("%s: %s" % (h[0], h[2]), LINE_CHARS)
    return _cap("%s:%d: %s" % (h[0], h[1], h[2].strip()), LINE_CHARS)


def shown_count(hits, budget, mode="content"):
    """How many hits to show: a PREFIX of file order, at most SHOW, and only while their lines fit in `budget`
    characters. The cut never depends on a score (KC-J5)."""
    n = used = 0
    for h in hits[:SHOW]:
        size = len(_hit_line(h, mode)) + 1
        if used + size > budget:
            break
        n, used = n + 1, used + size
    return n


_GREP_R_SKIPS = "; not searched, which grep -r reads: files that .gitignore or .ignore rules exclude, and binary files"
_GREP_C_ZEROS = "; files with no match are left out (grep -c prints each with :0)"


def format_answer(tool, spec, graft_q, graft_text, hits, cut, rerank=None):
    """The answer: what happened and how to get the raw result first, then graft's answer, then rg's result in the
    call's own mode (file names, counts or lines: VERIFY-JT3 F-2) in file order as far as it fits, then what was cut.
    A grep answer's count line says what grep would read that rg skipped (F-1). `rerank(shown) -> (order, note)` is
    the Jev switch; it only ever reorders shown lines."""
    mode = spec["mode"]
    files = list(dict.fromkeys(h[0] for h in hits))
    where = " ".join(spec["paths"]) or "."
    extras = "".join((" glob %s" % ",".join(spec["globs"]) if spec["globs"] else "",
                      " type %s" % spec["type"] if spec["type"] else "", " -i" if spec["i"] else "",
                      " -w" if spec["w"] else "",
                      {"names": ", file names only", "count": ", counts only"}.get(mode, "")))
    head = ("SEARCH INTERCEPT (search-intercept.py): this %s was answered here and did NOT run; %s."
            % ("Grep call" if tool == "Grep" else "Bash %s command" % spec["prog"], FIRST_LINE))
    out = [head, _cap("Search: %r in %s%s." % (spec["pattern"], where, extras), 400),
           "graft ask %s (lexical ranking; it may list near names):" % graft_q,
           _cap(graft_text or "(no answer)", GRAFT_CHARS)]
    at_least = "at least " if cut else ""
    if mode == "names":
        count = "%s%d file%s match%s" % (at_least, len(files), "" if len(files) == 1 else "s",
                                          "es" if len(files) == 1 else "")
    else:
        total = sum(h[1] for h in hits) if mode == "count" else len(hits)
        count = "%s%d %s%s in %d file%s" % (at_least, total, "matching line" if mode == "count" else "hit",
                                            "" if total == 1 else "s", len(files), "" if len(files) == 1 else "s")
    skips = ((_GREP_R_SKIPS if spec["r"] else "") + (_GREP_C_ZEROS if mode == "count" else "")
             if spec["prog"] == "grep" else "")
    unit = "file order" if mode == "content" else "path order"
    n = shown_count(hits, MAX_ANSWER - sum(len(x) + 1 for x in out) - CUT_RESERVE - len(skips), mode)
    order, note = list(range(n)), None
    if rerank is not None and mode == "content" and len(hits) > RANK_ABOVE and n > 1:
        order, note = rerank(hits[:n])
    if not hits:
        out.append("rg: 0 hits%s." % skips)
    elif n == len(hits) and not cut:
        out.append("rg: %s (all shown, %s%s)%s:" % (count, unit, "; " + note if note else "", skips))
    else:
        out.append("rg: %s; the first %d in %s%s%s:" % (count, n, unit, "; " + note if note else "", skips))
    out += [_hit_line(hits[i], mode) for i in order]
    rest = hits[n:]
    if rest or cut:
        if mode == "content":
            per = {}
            for h in rest:
                per[h[0]] = per.get(h[0], 0) + 1
            what, listing = ("%s%d more hit%s" % (at_least, len(rest), "" if len(rest) == 1 else "s"),
                             ", ".join("%s (%d)" % kv for kv in per.items()))
        else:
            what, listing = ("%s%d more file%s" % (at_least, len(rest), "" if len(rest) == 1 else "s"),
                             ", ".join(h[0] if mode == "names" else "%s (%d)" % h[:2] for h in rest))
        out.append(_cap("Cut: %s after the first %d, in %s; %s. By file: %s" % (
            what, n, unit, FIRST_LINE, listing or "-"), CUT_RESERVE - 100))
    text = "\n".join(out)
    if len(text) > MAX_ANSWER:              # a backstop only: the budget above keeps every answer under the cap
        text = text[:MAX_ANSWER - 70] + "\n[answer cut at %d characters; %s]" % (MAX_ANSWER, FIRST_LINE)
    return text


def answer_search(tool, spec, cwd, roots, deadline, jev_url, state_dir, tools, jev_on=False):
    """The condensed answer text. Raises on any failure of graft or rg (the caller fails open)."""
    graft, rg = tools
    scope = os.path.commonpath(roots) if roots else cwd
    rel = os.path.relpath(os.path.realpath(scope), os.path.realpath(ROOT))
    gargs = [graft, "ask", spec["pattern"], "-n", "5"] + (["--in", rel] if rel != "." else [])
    gproc = _spawn(gargs, ROOT)                                     # graft and rg run at the same time
    hits, cut = run_rg(rg, spec, cwd, roots, deadline)
    gtext = graft_answer(gproc, deadline)
    gq = "%r%s" % (spec["pattern"], " --in %s" % rel if rel != "." else "")
    rerank = (lambda shown: jev_reorder(shown, spec["pattern"], deadline, jev_url, state_dir)) if jev_on else None
    return format_answer(tool, spec, gq, gtext, hits, cut, rerank)


# ---------------------------------------------------------------- (c) the escape hatch

def seen_key(tool, tool_input):
    import hashlib
    body = {k: v for k, v in tool_input.items() if k != "description"}
    return hashlib.sha256(json.dumps([tool, body], sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _load_seen(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, (int, float))
            and not isinstance(v, bool)}


def seen_recently(state_dir, key, now):
    ts = _load_seen(os.path.join(state_dir, "intercept-seen.json")).get(key)
    return ts is not None and 0 <= now - ts <= WINDOW_S


def record_seen(state_dir, key, now):
    """Write the key BEFORE the block (0600, atomic). Raises when it cannot: the caller then does not block."""
    path = os.path.join(state_dir, "intercept-seen.json")
    if not os.path.isdir(state_dir):
        os.makedirs(state_dir, mode=0o700, exist_ok=True)
    data = {k: v for k, v in _load_seen(path).items() if 0 <= now - v <= PRUNE_S}
    data[key] = now
    tmp = "%s.%d.tmp" % (path, os.getpid())
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        os.write(fd, json.dumps(data, sort_keys=True).encode("utf-8"))
    finally:
        os.close(fd)
    os.replace(tmp, path)
    if _load_seen(path).get(key) != now:
        raise OSError("the seen record did not persist")


# ---------------------------------------------------------------- the hook

def _on_alarm(signum, frame):
    for proc in _children:
        _kill(proc, reap=False)
    os._exit(0)


def decide(payload, state_dir, jev_url, jev_on=False, now=None, deadline=None):
    """(exit code, stderr text) for one PreToolUse payload. main() turns any exception into exit 0."""
    now = time.time() if now is None else now
    deadline = time.monotonic() + HOOK_BUDGET_S - 2 if deadline is None else deadline
    tool = payload.get("tool_name")
    ti = payload.get("tool_input")
    if tool not in ("Grep", "Bash") or not isinstance(ti, dict):
        return 0, ""
    cwd = payload.get("cwd")
    cwd = cwd if isinstance(cwd, str) and os.path.isdir(cwd) else os.getcwd()
    message, spec = None, None
    if tool == "Bash":
        cmd = ti.get("command")
        if not isinstance(cmd, str) or not cmd.strip() or len(cmd) > MAX_CMD:
            return 0, ""
        p = Parsed(cmd)
        hit = quirk(p)
        if hit:
            message = quirk_message(*hit)
        else:
            spec = bash_search(p)
    else:
        spec = grep_tool_search(ti)
    if message is None:
        scope = semantic_scope(spec, cwd)
        if scope is None:
            return 0, ""
        import shutil
        tools = (shutil.which("graft"), shutil.which("rg"))
        if not all(tools):
            return 0, ""
    key = seen_key(tool, ti)
    if seen_recently(state_dir, key, now):
        return 0, ""
    if message is None:
        message = answer_search(tool, spec, scope[0], scope[1], deadline, jev_url, state_dir, tools, jev_on)
    record_seen(state_dir, key, now)
    return 2, message


def main():
    if os.environ.get("AF_SEARCH_INTERCEPT", "").strip() == "0":
        return 0
    state_dir = os.environ.get("AF_SEARCH_INTERCEPT_STATE") or os.path.join(ROOT, ".jev")
    jev_url = os.environ.get("AF_SEARCH_INTERCEPT_JEV_URL") or None
    if os.path.exists(os.path.join(state_dir, "intercept-off")):
        return 0
    jev_on = (os.environ.get("AF_SEARCH_INTERCEPT_JEV_RANK", "").strip() == "1"
              or os.path.exists(os.path.join(state_dir, "intercept-jev-rank-on")))
    signal.signal(signal.SIGALRM, _on_alarm)
    signal.alarm(HOOK_BUDGET_S)
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(payload, dict):
            return 0
        rc, text = decide(payload, state_dir, jev_url, jev_on)
    except BaseException:                   # fail open: no output, the tool call runs
        return 0
    finally:
        signal.alarm(0)
        for proc in _children:              # a failure after a spawn must not leave graft or rg running
            if proc.poll() is None:
                _kill(proc)
    if rc == 2 and text:
        sys.stderr.write(text + "\n")
        sys.stderr.flush()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
