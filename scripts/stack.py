#!/usr/bin/env python3
"""stack.py — run a stack: a named, fixed sequence of instrument calls with typed parameters, kept in the committed
registry scripts/stacks.toml and run in ONE tool call (task #339, D-103: "Create script stacks ... and then tie them
to specific labels"; design docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md §2-§5; the schema and the rules
are the CONTRACT of tasks/briefs/labeling/LS-B9-brief.md).

  python3 scripts/stack.py list                                  the catalog, one line per stack, its notes under it
  python3 scripts/stack.py catalog                               the SessionStart text: a heading, list, one line on
                                                                 ratings, under 4,000 characters; exit 0 always (on a
                                                                 failure, one line naming why)
  python3 scripts/stack.py explain LABEL key=value ...          the resolved plan; runs nothing, writes no record
  python3 scripts/stack.py LABEL key=value ... [--rate RUN[.STEP]=REL/USE]...   run the stack
  python3 scripts/stack.py rate RUN[.STEP]=REL/USE ...          ratings only (REL and USE are 0 to 3)
  --tree PATH: the target tree, a git toplevel (default: the toplevel of the current directory).
  For tests only: --registry PATH, --log-dir PATH, --transcript-root PATH.

Every parameter check runs before any step does. A step runs as an argument vector (never a shell) with cwd = the
target tree, stdin from /dev/null, in its own session; past its timeout its process group gets SIGTERM, then SIGKILL
3 s later. When a step's leader exits, whatever it left running in its process group is killed at once (a child left
behind would go on writing past the cap and the timeout). A program, [tools] entry or interpreter script that is
missing prints `unmapped — <tool> unavailable`, and so does a step whose output holds its `unmapped_if` text (a wrapper
that prints "missing" and exits 0 when its binary is absent; `tool` names the instrument). A step's saved output is
capped at its `save_cap_mb` (20 MB by default): past the cap the step's group gets SIGKILL at once (a grace would let
a writer fill the disk), the saved file ends in a marker line and the record says `truncated: true`.
Placeholders: {name} a scalar, {name*} a list spliced, {name*:FLAG} each element after FLAG, {name?:FLAG} FLAG and the
value when set, {name,} a list joined with commas into one element, {@step*} an earlier step's stdout lines (each a path
inside the tree or this run's dir). Built-ins: {tree} {run} {main} {head} {branch} {each} {transcript}, and {tmp}: a
per-run dir /tmp/stack-<run id>, outside every git work tree, made before the first step of a run that uses it and
removed after the run, on success, failure and signal alike.
Step fields beyond the obvious: `foreach = "<list param>"` or `foreach = "@<step>"` (one call per element, or per stdout
line of an earlier step, as {each}); `empty_ok = true` (a chained input that printed nothing leaves the step with
nothing to do: not selected, never a failure); `needs = ["<step>", ...]` (the step runs only when each named earlier
step ended ok); `headline = true` (the step's first stdout line, its control characters escaped and cut at 500
characters, goes into the print's header right after the tree line: the print cap cuts an over-long header from its
end, `params:` first, VERIFY-LS-B9 R3-F1). A stack may carry `notes`, one-line cautions `list` prints under its line.
A section over its cap_lines prints its first and its last lines (a verdict is often the last line) and names the
saved full output; the whole print is capped at 9,000 characters, cut from the largest section first. Each step's
full output (stdout, then a `--- stderr ---` block) is saved as <run dir>/<step>[.<n>].out; one JSON line per run
goes to runs.jsonl in the log dir, the MAIN tree's .jev/stacks/ (found through git's common dir, so a worktree logs to
the main tree, AF-AP-235's class). Every line is one write under flock of <log dir>/.lock. Only a stack declared
`rated = true` takes ratings.
The runner's own signals (INT, TERM, HUP) kill its live steps' process groups; a SIGKILL of the runner cannot, and
leaves its steps running (and its {tmp} dir in place).

exit: 0 every required step passed · 1 a required step did not · 2 a usage or parameter refusal · 3 a registry or log
error · 128+N the runner took signal N (its live steps are killed; no record is written).
"""
import argparse
import datetime
import fcntl
import fnmatch
import glob
import hashlib
import json
import os
import re
import secrets
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REGISTRY = os.path.join(HERE, "stacks.toml")
DEFAULT_TRANSCRIPT_ROOT = "/root/.claude/projects"
PRINT_CAP = 9000
KILL_GRACE_S = 3.0
REPEAT_MAX = 20
TEXT_MAX = 500
SAVE_CAP_MB = 20          # a step's saved output, by default (a runaway step must not fill a shared disk)
POLL_S = 0.1              # how often a running step's timeout and saved-output size are checked
TMP_BASE = "/tmp"         # {tmp} lives here: outside every git work tree

LABEL_RE = re.compile(r"[a-z][a-z0-9-]{1,23}")
NAME_RE = re.compile(r"[a-z][a-z0-9_]{0,23}")
VALUE_RE = {"symbol": re.compile(r"[A-Za-z_][A-Za-z0-9_.:]{0,127}"),
            "word": re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}"),
            "agent": re.compile(r"a[0-9a-f]{16}"),
            "int": re.compile(r"[0-9]{1,6}")}
RATE_RE = re.compile(r"(s-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6})(?:\.([a-z][a-z0-9_]{0,23}))?=([0-3])/([0-3])")
PH_RE = re.compile(r"\{([^{}]*)\}")
PH_BODY_RE = re.compile(r"(@)?([a-z][a-z0-9_]{0,23})(?:(\*)(?::([^{}]+))?|\?:([^{}]+)|(,))?")
SCALAR_TYPES = ("path", "symbol", "text", "word", "agent", "choice", "int")
LIST_TYPES = {"paths": "path", "symbols": "symbol", "words": "word"}
BUILTINS = ("tree", "run", "main", "head", "branch", "each", "transcript", "tmp")
DEFAULT_BUILTINS = ("tree", "main", "head", "branch")
INTERPRETER_RE = re.compile(r"python[0-9.]*|bash|sh|node")   # argv[1] of these is a script that must exist
STACK_KEYS = {"summary", "replaces", "outward", "rated", "params", "steps", "notes"}
NOTE_MAX = 300            # characters of one catalog note
CATALOG_CAP = 4000        # the SessionStart catalog stays under this: the harness swaps a hook text over 10,000
                          # characters for a 2,000-character preview of its head (AF-AP-183)
# C0 and C1 control characters, DEL and the two Unicode line separators: a headline shows each as an escape (a CR or
# an ESC copied raw lets a step's output overwrite the header line in a terminal, VERIFY-LS-B9 R3-F5)
CONTROL_RE = re.compile("[\x00-\x1f\x7f-\x9f" + chr(0x2028) + chr(0x2029) + "]")
PARAM_KEYS = {"type", "required", "default", "choices", "split_from"}
STEP_KEYS = {"id", "argv", "group", "timeout", "cap_lines", "ok_rc", "required", "when", "repeat", "foreach",
             "unmapped_if", "tool", "save_cap_mb", "empty_ok", "needs", "headline"}
EACH_LINE = "\x00each\x00"  # {each} of a `foreach = "@step"` call until its line is known (no value or line holds a NUL)
HEADLINE_MAX = 500          # characters of a headline step's first line that go into the header
# split_from: the word-shaped tokens of the text, 3+ characters, minus these (owner_rulings.py matches ANY word as a
# substring, so "the" or "how" would match nearly every row)
WORD_TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")
SPLIT_STOP = frozenset("the and for not with this that from are was were has have had but its into when then than any "
                       "all can may one two out off per via use used using who what how why where which does did done "
                       "also about should would could will".split())

_HOME = os.path.expanduser("~")
_DENY_BASES = ("/root/.codiv", "/root/.claude/projects", "/root/.config/session-export",
               os.path.join(_HOME, ".codiv"), os.path.join(_HOME, ".claude", "projects"),
               os.path.join(_HOME, ".config", "session-export"))
DENY_DIRS = tuple(sorted({d for b in _DENY_BASES for d in (b, os.path.realpath(b))}))
QWEN_CONFIG_DIRS = tuple(sorted({d for b in ("/root/.config", os.path.join(_HOME, ".config"))
                                 for d in (b, os.path.realpath(b))}))


class Refusal(Exception):
    """A refusal and its exit code: 2 usage or parameter, 3 registry or log."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class Interrupted(Exception):
    def __init__(self, signum):
        super().__init__("signal %d" % signum)
        self.signum = signum


# ---------- the registry ----------

def _bad(where, message):
    raise Refusal(3, "registry: %s: %s" % (where, message))


def _keys(table, allowed, where):
    if not isinstance(table, dict):
        _bad(where, "must be a table")
    extra = sorted(set(table) - allowed)
    if extra:
        _bad(where, "unknown key(s) %s (allowed: %s)" % (", ".join(extra), ", ".join(sorted(allowed))))


def _int(value, lo, hi, where):
    if type(value) is not int or not lo <= value <= hi:
        _bad(where, "must be an integer from %d to %d (found %r)" % (lo, hi, value))
    return value


def _bool(value, where):
    if type(value) is not bool:
        _bad(where, "must be true or false (found %r)" % (value,))
    return value


class Param:
    def __init__(self, name, spec, where):
        self.where = where
        if not NAME_RE.fullmatch(name):
            _bad(where, "a parameter name matches ^[a-z][a-z0-9_]{0,23}$")
        _keys(spec, PARAM_KEYS, where)
        self.name, self.type = name, spec.get("type")
        if self.type not in SCALAR_TYPES and self.type not in LIST_TYPES:
            _bad(where + ".type", "one of %s (found %r)" % (" ".join(SCALAR_TYPES + tuple(LIST_TYPES)), self.type))
        self.required = _bool(spec.get("required", False), where + ".required")
        self.default, self.choices, self.split_from = spec.get("default"), spec.get("choices"), spec.get("split_from")
        if self.choices is not None and self.type != "choice":
            _bad(where + ".choices", "only a choice parameter has choices")
        if self.type == "choice" and not (isinstance(self.choices, list) and self.choices
                                          and all(isinstance(c, str) and c and not c.startswith("-") for c in self.choices)
                                          and len(set(self.choices)) == len(self.choices)):
            _bad(where + ".choices", "a choice parameter needs a list of distinct non-empty strings")
        if self.split_from is not None:
            if self.type != "words" or not isinstance(self.split_from, str):
                _bad(where + ".split_from", "only a words parameter is derived, from a text parameter's name")
            if self.required or self.default is not None:
                _bad(where, "a derived parameter takes no required and no default")
        if self.default is not None:
            if not isinstance(self.default, str):
                _bad(where + ".default", "must be a string")
            if self.required:
                _bad(where, "a required parameter takes no default")
            names = PH_RE.findall(self.default)
            if any(n not in DEFAULT_BUILTINS for n in names):
                _bad(where + ".default", "may name only {tree}, {main}, {head} or {branch}")
            if not names:
                try:
                    validate(self, self.default, None)
                except Refusal as e:
                    _bad(where + ".default", str(e))

    @property
    def is_list(self):
        return self.type in LIST_TYPES


def parse_element(text, where):
    """One argv element: ("lit", s) | ("tmpl", s) | ("splice", name, flag) | ("opt", name, flag) | ("chain", step).
    A tmpl holds scalar placeholders {name} and joins {name,}: each fills to one string."""
    found = list(PH_RE.finditer(text))
    if "{" in PH_RE.sub("", text) or "}" in PH_RE.sub("", text):
        _bad(where, "an unbalanced brace in %r" % text)
    if not found:
        return ("lit", text)
    kinds = []
    for m in found:
        b = PH_BODY_RE.fullmatch(m.group(1))
        if not b:
            _bad(where, "an unknown placeholder %s" % m.group(0))
        chain, name, star, star_flag, opt_flag, comma = b.groups()
        if chain:
            if not star or star_flag:
                _bad(where, "a chained input is written {@step*}")
            kinds.append(("chain", name))
        elif star:
            kinds.append(("splice", name, star_flag))
        elif opt_flag is not None:
            kinds.append(("opt", name, opt_flag))
        else:
            kinds.append(("join" if comma else "scalar", name))
    whole = len(found) == 1 and found[0].group(0) == text
    if whole and kinds[0][0] not in ("scalar", "join"):
        return kinds[0]
    if any(k[0] not in ("scalar", "join") for k in kinds):
        _bad(where, "%r: a list, optional or chained placeholder is the whole argv element" % text)
    return ("tmpl", text)


class Step:
    def __init__(self, spec, where, stack):
        _keys(spec, STEP_KEYS, where)
        sid = spec.get("id")
        if not isinstance(sid, str) or not NAME_RE.fullmatch(sid):
            _bad(where + ".id", "a step id matches ^[a-z][a-z0-9_]{0,23}$")
        self.id = sid
        self.where = where = "%s (%s)" % (where, sid)
        argv = spec.get("argv")
        if not (isinstance(argv, list) and argv and all(isinstance(a, str) and a for a in argv)):
            _bad(where + ".argv", "must be a non-empty list of non-empty strings")
        if "{" in argv[0] or "}" in argv[0]:
            _bad(where + ".argv", "argv[0], the program, is fixed by the registry: no placeholder")
        self.group = _int(spec.get("group", 1), 1, 99, where + ".group")
        self.timeout = _int(spec.get("timeout", 60), 1, 3600, where + ".timeout")
        self.cap_lines = _int(spec.get("cap_lines", 40), 1, 10000, where + ".cap_lines")
        ok_rc = spec.get("ok_rc", [0])
        if not (isinstance(ok_rc, list) and ok_rc and all(type(x) is int and 0 <= x <= 255 for x in ok_rc)):
            _bad(where + ".ok_rc", "must be a non-empty list of exit codes 0 to 255")
        self.ok_rc = tuple(ok_rc)
        self.required = _bool(spec.get("required", True), where + ".required")
        self.when = spec.get("when", {})
        if not isinstance(self.when, dict):
            _bad(where + ".when", "must be a table of parameter = value")
        for name, want in self.when.items():
            p = stack.params.get(name)
            if p is None or not isinstance(want, str):
                _bad(where + ".when", "%r: a parameter of this stack, matched against a string" % name)
            if p.is_list and want not in ("*", ""):
                _bad(where + ".when", "a list parameter matches only \"*\" (set) or \"\" (unset)")
            if p.type == "choice" and want not in ("*", "") and want not in p.choices:
                _bad(where + ".when", "%r is not one of %s's choices" % (want, name))
        self.foreach = spec.get("foreach")
        self.foreach_chain = None               # foreach = "@step": one call per stdout line of that earlier step
        if isinstance(self.foreach, str) and self.foreach.startswith("@"):
            self.foreach_chain, self.foreach = self.foreach[1:], None
            if not NAME_RE.fullmatch(self.foreach_chain):
                _bad(where + ".foreach", "\"@<step id>\" names an earlier step whose stdout lines are the calls")
        elif self.foreach is not None and not (isinstance(self.foreach, str) and self.foreach in stack.params
                                               and stack.params[self.foreach].is_list):
            _bad(where + ".foreach", "must name a list parameter of this stack, or \"@<step id>\"")
        self.repeat = self._repeat(spec.get("repeat"), stack)
        if (self.foreach is not None or self.foreach_chain is not None) and self.repeat is not None:
            _bad(where, "a step takes repeat or foreach, not both")
        self.empty_ok = _bool(spec.get("empty_ok", False), where + ".empty_ok")
        self.headline = _bool(spec.get("headline", False), where + ".headline")
        self.needs = spec.get("needs", [])
        if not (isinstance(self.needs, list) and all(isinstance(n, str) and NAME_RE.fullmatch(n) for n in self.needs)
                and len(set(self.needs)) == len(self.needs)):
            _bad(where + ".needs", "a list of distinct step ids")
        self.unmapped_if = spec.get("unmapped_if")
        if self.unmapped_if is not None and not (isinstance(self.unmapped_if, str) and self.unmapped_if.strip()
                                                 and "\n" not in self.unmapped_if):
            _bad(where + ".unmapped_if", "a literal output text of one line")
        self.tool = spec.get("tool")
        if self.tool is not None and not (isinstance(self.tool, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,40}", self.tool)
                                          and self.unmapped_if is not None):
            _bad(where + ".tool", "the name unmapped_if reports, a word of 1 to 40 characters (it needs unmapped_if)")
        self.save_cap_mb = _int(spec.get("save_cap_mb", SAVE_CAP_MB), 1, 1024, where + ".save_cap_mb")
        self.elems = [parse_element(a, where + ".argv") for a in argv]
        self.chains = [e[1] for e in self.elems if e[0] == "chain"]
        names = [m.group(1) for e in self.elems if e[0] == "tmpl" for m in PH_RE.finditer(e[1])]
        self.uses_transcript = "transcript" in names and "transcript" not in stack.params
        for joined in [n[:-1] for n in names if n.endswith(",")]:
            p = stack.params.get(joined)
            if p is None or not p.is_list:
                _bad(where + ".argv", "{%s,} must name a list parameter" % joined)
            if not stack.set_for(self, joined):
                _bad(where + ".argv", "{%s,} is optional with no default: guard the step with when %s = \"*\""
                     % (joined, joined))
        names = [n for n in names if not n.endswith(",")]
        for name in names:
            p = stack.params.get(name)
            if p is not None:
                if p.is_list:
                    _bad(where + ".argv", "{%s} is a list: write {%s*}" % (name, name))
                if not stack.set_for(self, name):
                    _bad(where + ".argv", "{%s} is optional with no default: guard the step with when %s = \"*\""
                         % (name, name))
            elif name not in BUILTINS:
                _bad(where + ".argv", "{%s} is neither a parameter nor a built-in (%s)" % (name, ", ".join(BUILTINS)))
            elif name == "each" and self.foreach is None and self.foreach_chain is None:
                _bad(where + ".argv", "{each} needs foreach")
        for e in self.elems:
            p = stack.params.get(e[1]) if e[0] in ("splice", "opt") else None
            if e[0] == "splice" and (p is None or not p.is_list):
                _bad(where + ".argv", "{%s*} must name a list parameter" % e[1])
            if e[0] == "opt" and (p is None or p.is_list):
                _bad(where + ".argv", "{%s?:...} must name a scalar parameter" % e[1])
        if (self.foreach is not None or self.foreach_chain is not None) and "each" not in names:
            _bad(where + ".argv", "a foreach step uses {each}")
        if self.empty_ok and not (self.chains or self.foreach_chain):
            _bad(where + ".empty_ok", "only a step with a chained input ({@step*} or foreach = \"@step\") can be empty")

    def sources(self):
        """The earlier steps this step reads or waits for: its chained inputs, its foreach source, its needs."""
        return self.chains + ([self.foreach_chain] if self.foreach_chain else []) + self.needs

    def _repeat(self, rep, stack):
        if rep is None:
            return None
        if type(rep) is int:
            return _int(rep, 1, REPEAT_MAX, self.where + ".repeat")
        m = re.fullmatch(r"\{([a-z][a-z0-9_]{0,23})\}", rep) if isinstance(rep, str) else None
        p = stack.params.get(m.group(1)) if m else None
        if p is None or p.type not in ("choice", "int"):
            _bad(self.where + ".repeat", "an integer, or {name} of a choice or int parameter")
        if p.type == "choice" and not all(re.fullmatch(r"[0-9]{1,2}", c) and 1 <= int(c) <= REPEAT_MAX
                                          for c in p.choices):
            _bad(self.where + ".repeat", "every choice of %s must be a count from 1 to %d" % (p.name, REPEAT_MAX))
        if not stack.set_for(self, p.name):
            _bad(self.where + ".repeat", "%s is optional with no default" % p.name)
        return p.name


class Stack:
    def __init__(self, label, spec):
        where = "stacks.%s" % label
        if not LABEL_RE.fullmatch(label):
            _bad(where, "a label matches ^[a-z][a-z0-9-]{1,23}$")
        _keys(spec, STACK_KEYS, where)
        if spec.get("outward") is True:
            _bad(where, "outward = true: a stack that takes an outward action is refused")
        if spec.get("outward") is not False:
            _bad(where + ".outward", "must be declared false")
        for key in ("summary", "replaces"):
            if not isinstance(spec.get(key), str) or not spec[key].strip() or "\n" in spec[key]:
                _bad(where + "." + key, "must be one non-empty line")
        self.label, self.summary, self.replaces = label, spec["summary"], spec["replaces"]
        self.rated = _bool(spec.get("rated", False), where + ".rated")   # only a rated stack takes ratings
        self.notes = spec.get("notes", [])
        if not (isinstance(self.notes, list) and all(isinstance(n, str) and n.strip() and len(n) <= NOTE_MAX
                                                     and not CONTROL_RE.search(n) for n in self.notes)):
            _bad(where + ".notes", "a list of notes of 1 to %d characters, each one line with no control character"
                 % NOTE_MAX)
        params = spec.get("params", {})
        if not isinstance(params, dict):
            _bad(where + ".params", "must be a table")
        self.params = {name: Param(name, p, "%s.params.%s" % (where, name)) for name, p in params.items()}
        for p in self.params.values():
            if p.split_from is not None and getattr(self.params.get(p.split_from), "type", None) != "text":
                _bad(p.where + ".split_from", "must name a text parameter of this stack")
        agents = [p.name for p in self.params.values() if p.type == "agent"]
        self.agent = agents[0] if len(agents) == 1 else None
        steps = spec.get("steps")
        if not (isinstance(steps, list) and steps):
            _bad(where + ".steps", "must hold at least one step")
        self.steps = []
        for i, s in enumerate(steps):
            st = Step(s, "%s.steps[%d]" % (where, i), self)
            if any(o.id == st.id for o in self.steps):
                _bad(st.where, "the id repeats")
            if st.uses_transcript and (self.agent is None or not self.set_for(st, self.agent)):
                _bad(st.where, "{transcript} needs exactly one agent parameter, set for this step")
            self.steps.append(st)
        by_id = {s.id: s for s in self.steps}
        for st in self.steps:
            for src in st.chains:
                if src not in by_id or by_id[src].group >= st.group:
                    _bad(st.where, "{@%s*} must name a step of an earlier group" % src)
            for src, what in ([(st.foreach_chain, "foreach = \"@%s\"")] if st.foreach_chain else []) + [
                    (n, "needs %s") for n in st.needs]:
                if src not in by_id or by_id[src].group >= st.group:
                    _bad(st.where, (what + " must name a step of an earlier group") % src)
        self.groups = sorted({s.group for s in self.steps})

    def set_for(self, step, name):
        """True when the parameter always holds a value when the step runs."""
        p = self.params[name]
        want = step.when.get(name)
        return p.required or p.default is not None or (want is not None and want != "")

    def settable(self):
        return [n for n, p in self.params.items() if p.split_from is None]


def load_registry(path):
    """({tool: [candidates]}, {label: Stack}); any defect -> Refusal(3)."""
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except OSError as e:
        raise Refusal(3, "registry %s: %s" % (path, e.strerror or e))
    except tomllib.TOMLDecodeError as e:
        raise Refusal(3, "registry %s: %s" % (path, e))
    _keys(data, {"version", "tools", "stacks"}, "the top level")
    if type(data.get("version")) is not int or data["version"] != 1:
        _bad("version", "must be 1 (found %r)" % (data.get("version"),))
    tools = data.get("tools", {})
    if not isinstance(tools, dict) or not all(isinstance(c, list) and c and all(isinstance(x, str) and x for x in c)
                                              for c in tools.values()):
        _bad("tools", "tool name = a non-empty list of paths or program names")
    stacks = data.get("stacks")
    if not (isinstance(stacks, dict) and stacks):
        _bad("stacks", "must hold at least one stack")
    return tools, {label: Stack(label, spec) for label, spec in stacks.items()}


# ---------- values ----------

def _inside(path, root):
    return path == root or path.startswith(root.rstrip("/") + "/")


def deny_rule(path):
    """The deny-list entry an absolute path hits, or None."""
    parts = path.split("/")
    base = parts[-1].lower()
    if base == ".pc-bridge.env":
        return ".pc-bridge.env"
    if fnmatch.fnmatchcase(base, "*.env"):
        return "*.env"
    if ".git" in parts:
        return ".git/"
    for d in DENY_DIRS:
        if _inside(path, d):
            return d + "/"
    for cfg in QWEN_CONFIG_DIRS:
        if path.startswith(cfg + "/") and fnmatch.fnmatchcase(path[len(cfg) + 1:].split("/")[0], "qwen-*"):
            return "~/.config/qwen-*"
    return None


def check_path(raw, tree, what, run_dir=None):
    """The tree-relative form of a path value; refused (exit 2) when it is empty, an option, on the deny list, or
    outside the tree lexically or once resolved. tree None: the checks that need no tree (a registry default).
    run_dir (chained lines only): a path inside this run's own dir is accepted too, in its absolute form (the run dir
    is outside the target tree for a worktree or an explicit --log-dir)."""
    if not raw:
        raise Refusal(2, "%s refused: an empty path" % what)
    if raw.startswith("-"):
        raise Refusal(2, "%s refused: %r begins with '-' (option injection)" % (what, raw))
    if any(c in raw for c in "\x00\n\r"):
        raise Refusal(2, "%s refused: %r holds a NUL or a newline" % (what, raw))
    base = tree or "/"
    lexical = os.path.normpath(os.path.join(base, raw))
    real = os.path.realpath(os.path.join(base, raw))
    for p in (lexical, real) if tree else (lexical,):
        rule = deny_rule(p)
        if rule:
            raise Refusal(2, "%s refused: %r is on the deny list (%s)" % (what, raw, rule))
    if tree is None:
        return raw
    if run_dir is not None and _inside(lexical, run_dir) and _inside(real, os.path.realpath(run_dir)):
        return lexical
    if not _inside(lexical, tree):
        raise Refusal(2, "%s refused: %r is outside the tree %s" % (what, raw, tree))
    if not _inside(real, tree):
        raise Refusal(2, "%s refused: %r resolves outside the tree %s (to %s)" % (what, raw, tree, real))
    return os.path.relpath(lexical, tree)


def check_scalar(kind, raw, tree, what, choices=None):
    if kind == "path":
        return check_path(raw, tree, what)
    if kind == "text":
        if not 1 <= len(raw) <= TEXT_MAX:
            raise Refusal(2, "%s refused: a text is 1 to %d characters (found %d)" % (what, TEXT_MAX, len(raw)))
        if any(c in raw for c in "\x00\n\r"):
            raise Refusal(2, "%s refused: a text holds no NUL and no newline" % what)
        if raw.startswith("-"):
            raise Refusal(2, "%s refused: %r begins with '-' (option injection)" % (what, raw))
        return raw
    if kind == "choice":
        if raw not in choices:
            raise Refusal(2, "%s refused: %r is not one of %s" % (what, raw, "|".join(choices)))
        return raw
    if not VALUE_RE[kind].fullmatch(raw):
        raise Refusal(2, "%s refused: %r is not a valid %s (%s)" % (what, raw, kind, VALUE_RE[kind].pattern))
    return raw


def validate(p, raw, tree):
    """A parameter's value: a string, or a list of strings for a list type."""
    what = "%s=%s" % (p.name, raw if len(raw) <= 80 else raw[:77] + "...")
    if p.is_list:
        items = raw.split(",")
        if any(not x for x in items):
            raise Refusal(2, "%s refused: an empty element in the comma-separated list" % what)
        return [check_scalar(LIST_TYPES[p.type], x, tree, what) for x in items]
    return check_scalar(p.type, raw, tree, what, p.choices)


def derive_words(text):
    out, seen = [], set()
    for token in WORD_TOKEN_RE.findall(text):
        token = token.rstrip(".-")
        low = token.lower()
        if len(token) < 3 or low in SPLIT_STOP or low in seen or not VALUE_RE["word"].fullmatch(token):
            continue
        seen.add(low)
        out.append(token)
    return out


def git_out(cwd, *args):
    """git's stdout (stripped), or None when git fails."""
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def resolve_tree(opt):
    start = os.path.abspath(opt) if opt else os.getcwd()
    top = git_out(start, "rev-parse", "--show-toplevel")
    if not top:
        raise Refusal(2, "--tree %s: not inside a git work tree" % start)
    top = os.path.realpath(top)
    if opt and os.path.realpath(start) != top:
        raise Refusal(2, "--tree %s: not a toplevel (its toplevel is %s)" % (opt, top))
    return top


class Env:
    """The built-ins a run resolves once: tree, main, head, branch, transcript; run and tmp are set by the caller
    (tmp_used records whether a selected step names {tmp}, so only such a run makes the dir)."""

    def __init__(self, tree, opts, stack, values):
        self.tree, self.opts, self.stack, self.values = tree, opts, stack, values
        self.run = self.tmp = None
        self.tmp_used = False
        self._cache = {}

    def get(self, name):
        if name not in self._cache:
            self._cache[name] = getattr(self, "_" + name)()
        return self._cache[name]

    def _tree(self):
        return self.tree

    def _main(self):
        common = git_out(self.tree, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if not common:
            raise Refusal(3, "the main tree: git rev-parse --git-common-dir failed in %s" % self.tree)
        return os.path.dirname(os.path.realpath(common))

    def _head(self):
        head = git_out(self.tree, "rev-parse", "HEAD")
        if not head:
            raise Refusal(2, "{head}: HEAD does not resolve in %s" % self.tree)
        return head

    def _branch(self):
        branch = git_out(self.tree, "symbolic-ref", "--short", "-q", "HEAD")
        if not branch:
            raise Refusal(2, "{branch}: HEAD is detached in %s; pass the branch" % self.tree)
        return branch

    def _transcript(self):
        agent = self.values[self.stack.agent]
        pattern = os.path.join(glob.escape(self.opts.transcript_root), "*", "*", "subagents", "agent-%s.jsonl" % agent)
        hits = sorted(glob.glob(pattern))
        if len(hits) != 1:
            raise Refusal(2, "{transcript}: %d matches of %s; exactly one is needed" % (len(hits), pattern))
        return hits[0]

    def head_or_none(self):
        try:
            return self.get("head")
        except Refusal:
            return None


def parse_tokens(stack, tokens, tree, env):
    settable = stack.settable()
    known = "known keys: %s" % (", ".join(settable) or "(none)")
    given = {}
    for token in tokens:
        key, eq, value = token.partition("=")
        if not eq:
            raise Refusal(2, "%r is not a key=value token; %s" % (token, known))
        if key not in stack.params:
            raise Refusal(2, "unknown key %r for stack %s; %s" % (key, stack.label, known))
        if key not in settable:
            raise Refusal(2, "%s is derived from %s, never set; %s" % (key, stack.params[key].split_from, known))
        if key in given:
            raise Refusal(2, "repeated key %r; %s" % (key, known))
        given[key] = value
    values = {}
    for name in settable:
        p = stack.params[name]
        if name in given:
            raw = given[name]
        elif p.required:
            raise Refusal(2, "missing required key %r for stack %s; %s" % (name, stack.label, known))
        elif p.default is not None:
            raw = PH_RE.sub(lambda m: env.get(m.group(1)), p.default)
        else:
            continue
        values[name] = validate(p, raw, tree)
    for name, p in stack.params.items():
        if p.split_from is not None and p.split_from in values:
            words = derive_words(values[p.split_from])
            if words:
                values[name] = words
    return values


def parse_ratings(specs):
    out = []
    for spec in specs:
        m = RATE_RE.fullmatch(spec)
        if not m:
            raise Refusal(2, "rating %r: the form is RUN[.STEP]=REL/USE, RUN s-<yyyymmddTHHMMSSZ>-<6 hex>, "
                             "REL and USE 0 to 3" % spec)
        out.append({"run": m.group(1), "step": m.group(2), "rel": int(m.group(3)), "use": int(m.group(4))})
    return out


# ---------- the plan ----------

def unselected(step, values):
    """Why the step does not run with these values, or None when it runs."""
    for name, want in step.when.items():
        value = values.get(name)
        is_set = value is not None and value != []
        ok = is_set if want == "*" else (not is_set if want == "" else value == want)
        if not ok:
            return "when %s=%s" % (name, want if want else "''")
    if step.foreach is not None and not values.get(step.foreach):
        return "foreach %s is empty" % step.foreach
    return None


def invocations(step, values):
    """[(n or None, each or None)]: foreach elements, repeat numbers, or one plain call. A `foreach = "@step"` step has one
    placeholder call here; the runner makes one call per line of that step when the line is known."""
    if step.foreach_chain is not None:
        return [(None, EACH_LINE)]
    if step.foreach is not None:
        return [(i + 1, e) for i, e in enumerate(values[step.foreach])]
    count = 1
    if isinstance(step.repeat, int):
        count = step.repeat
    elif step.repeat is not None:
        count = int(values[step.repeat])
        if not 1 <= count <= REPEAT_MAX:
            raise Refusal(2, "%s=%s: a repeat count is 1 to %d" % (step.repeat, values[step.repeat], REPEAT_MAX))
    return [(i + 1 if count > 1 else None, None) for i in range(count)]


def pre_resolve(step, values, env, each):
    """The argv with every placeholder but {@step*} filled; a chained input stays as ("chain", step)."""
    def scalar(name):
        if name.endswith(","):          # no element holds a comma: a list value is split on commas (validate)
            return ",".join(values.get(name[:-1], []))
        if name in env.stack.params:
            return values[name]
        if name == "each":
            return each
        if name == "run":
            return env.run
        if name == "tmp":
            env.tmp_used = True
            return env.tmp
        return env.get(name)

    parts = []
    for e in step.elems:
        if e[0] == "lit":
            parts.append(e[1])
        elif e[0] == "tmpl":
            parts.append(PH_RE.sub(lambda m: scalar(m.group(1)), e[1]))
        elif e[0] == "splice":
            for item in values.get(e[1], []):
                parts += [e[2], item] if e[2] else [item]
        elif e[0] == "opt":
            if e[1] in values:
                parts += [e[2], values[e[1]]]
        else:
            parts.append(e)
    return parts


def shown(parts):
    """The parts as a record shows them: a chained input as <lines of STEP>, a foreach line not yet known as {each}."""
    return [p.replace(EACH_LINE, "{each}") if isinstance(p, str) else "<lines of %s>" % p[1] for p in parts]


def display(parts):
    return " ".join("<lines of %s>" % p[1] if isinstance(p, tuple) else shlex.quote(p.replace(EACH_LINE, "{each}"))
                    for p in parts)


def build_plan(stack, values, env):
    """[(step, [(n, each, parts)] or None, why not selected or None)] in registry order; every check runs here."""
    plan = []
    for step in stack.steps:
        why = unselected(step, values)
        if why:
            plan.append((step, None, why))
            continue
        plan.append((step, [(n, each, pre_resolve(step, values, env, each)) for n, each in invocations(step, values)],
                     None))
    return plan


# ---------- running ----------

class Result:
    def __init__(self, step, n, argv, status, rc=None, secs=0.0, note=None):
        self.step, self.n, self.argv, self.status, self.rc, self.secs, self.note = step, n, argv, status, rc, secs, note
        self.out = self.sha = None
        self.nbytes = 0
        self.stdout = ""
        self.text = ""
        self.truncated = False
        self.strays = False      # its leader exited and left processes running in its group; the runner killed them


class Runner:
    def __init__(self, tree, run_dir, tools):
        self.tree, self.run_dir, self.tools = tree, run_dir, tools
        self.results = {}
        self.idle = {}           # step id -> why it had nothing to do (an empty_ok step whose input printed nothing)
        self.live = set()
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.threads = []

    def resolve_program(self, argv):
        """(argv to execute, None) or (None, the missing tool)."""
        prog = argv[0]
        if prog in self.tools:
            for cand in self.tools[prog]:
                c = os.path.expanduser(cand)
                path = c if "/" in c else shutil.which(c)
                if path and os.path.isfile(path) and os.access(path, os.X_OK):
                    return [path] + argv[1:], None
            return None, prog
        if "/" in prog:
            path = prog if os.path.isabs(prog) else os.path.join(self.tree, prog)
            if not (os.path.isfile(path) and os.access(path, os.X_OK)):
                return None, prog
        elif shutil.which(prog) is None:
            return None, prog
        if INTERPRETER_RE.fullmatch(os.path.basename(prog)) and len(argv) > 1 and not argv[1].startswith("-"):
            script = argv[1] if os.path.isabs(argv[1]) else os.path.join(self.tree, argv[1])
            if not os.path.isfile(script):
                return None, argv[1]
        return argv, None

    def not_ok(self, src):
        """None when every result of step src is ok; else what went wrong, for a step that reads or waits for it."""
        results = self.results.get(src)
        if not results:
            return "did not run"
        for r in results:
            if r.status != "ok":
                return {"failed": "failed (rc %s)" % r.rc, "timeout": "timed out", "unmapped": "was unmapped",
                        "skipped": "was skipped"}[r.status]
        return None

    def chain_input(self, src):
        """(the source step's stdout lines as paths, None); ([], None) when it printed nothing; or (None, why this step
        is skipped). A line is a path inside the tree (tree-relative) or inside this run's own dir (absolute); a
        truncated source feeds nothing."""
        bad = self.not_ok(src)
        if bad:
            return None, "its input step %s %s" % (src, bad)
        results = self.results[src]
        if any(r.truncated for r in results):
            return None, "its input step %s was truncated at its save cap" % src
        lines = [ln.rstrip("\r") for r in results for ln in r.stdout.split("\n") if ln.strip()]
        try:
            return [check_path(ln, self.tree, "a line of %s" % src, run_dir=self.run_dir) for ln in lines], None
        except Refusal as e:
            return None, str(e)

    def run_step(self, step, invs):
        """Every invocation of one step, in order, each result kept as it comes. A defect of the runner itself (an
        exception in this thread) fails the step loudly: a thread that died silently would drop the step from the
        record and from the exit code, a hollow green."""
        results = self.results.setdefault(step.id, [])
        try:
            chains, why, empty = {}, None, None
            for src in step.chains + ([step.foreach_chain] if step.foreach_chain else []):
                lines, why = self.chain_input(src)
                if why:
                    break
                if not lines:
                    empty = src
                    break
                chains[src] = lines
            if why is None and empty is not None:
                if step.empty_ok:         # nothing to do: listed as not selected, never a failure (before needs)
                    self.idle[step.id] = "its input step %s printed nothing" % empty
                    return
                why = "its input step %s printed nothing" % empty
            for need in [] if why else step.needs:
                bad = self.not_ok(need)
                if bad:
                    why = "its prerequisite step %s %s" % (need, bad)
                    break
            if why is None and step.foreach_chain is not None:     # one call per line, {each} = the line
                parts0 = invs[0][2]
                invs = [(i + 1, line, [p.replace(EACH_LINE, line) if isinstance(p, str) else p for p in parts0])
                        for i, line in enumerate(chains[step.foreach_chain])]
            for n, each, parts in invs:
                out = os.path.join(self.run_dir, "%s%s.out" % (step.id, "" if n is None else ".%d" % n))
                if why is None and self.stop.is_set():
                    why = "the runner was interrupted"
                if why is not None:
                    r = Result(step, n, shown(parts), "skipped", note=why)
                    self.save(r, out, ("SKIPPED — %s\n" % why).encode(), b"")
                else:
                    argv = [x for p in parts for x in (chains[p[1]] if isinstance(p, tuple) else [p])]
                    r = self.execute(step, n, argv, out)
                results.append(r)
        except BaseException as e:
            note = "the runner failed: %s: %s" % (type(e).__name__, e)
            r = Result(step, None, shown(invs[0][2]), "failed", note=note)
            try:
                self.save(r, os.path.join(self.run_dir, "%s.runner-error.out" % step.id), (note + "\n").encode(), b"")
            except OSError:
                pass
            results.append(r)

    def execute(self, step, n, argv, out):
        run_argv, missing = self.resolve_program(argv)
        if missing is not None:
            r = Result(step, n, argv, "unmapped", note=missing)
            self.save(r, out, ("unmapped — %s unavailable\n" % missing).encode(), b"")
            return r
        cap = step.save_cap_mb * 1024 * 1024
        t0 = time.monotonic()
        timed_out = over_cap = False
        with open(out + ".stdout", "wb") as fo, open(out + ".stderr", "wb") as fe:
            with self.lock:
                if self.stop.is_set():
                    proc = None
                else:
                    try:
                        proc = subprocess.Popen(run_argv, cwd=self.tree, stdin=subprocess.DEVNULL, stdout=fo, stderr=fe,
                                                start_new_session=True, close_fds=True)
                    except FileNotFoundError:
                        proc = "unmapped"
                    except OSError as e:
                        proc = e
                    else:
                        self.live.add(proc)
            if not isinstance(proc, subprocess.Popen):
                if proc == "unmapped":
                    r = Result(step, n, run_argv, "unmapped", note=run_argv[0])
                    text = "unmapped — %s unavailable\n" % run_argv[0]
                else:
                    why = "the runner was interrupted" if proc is None else "cannot start: %s" % proc
                    r = Result(step, n, run_argv, "skipped" if proc is None else "failed", note=why)
                    text = why + "\n"
                fo.write(text.encode())
                fo.flush()
            else:
                deadline = t0 + step.timeout
                strays = False
                try:
                    while True:       # the timeout and the saved-output cap, checked every POLL_S
                        try:
                            rc = proc.wait(timeout=POLL_S)
                            break
                        except subprocess.TimeoutExpired:
                            pass
                        if time.monotonic() >= deadline:
                            timed_out = True
                            kill_groups([proc])
                        elif os.fstat(fo.fileno()).st_size + os.fstat(fe.fileno()).st_size > cap:
                            over_cap = True
                            kill_groups([proc], grace=None)   # SIGKILL at once: a grace lets a writer fill the disk
                        else:
                            continue
                        rc = proc.returncode
                        break
                    if not (timed_out or over_cap) and _group_alive(proc.pid):
                        strays = True     # the leader exited and left its group running: nothing may write on
                        _signal_group(proc.pid, signal.SIGKILL)
                finally:
                    with self.lock:
                        self.live.discard(proc)
                if timed_out:
                    r = Result(step, n, run_argv, "timeout", rc=rc, secs=time.monotonic() - t0)
                elif over_cap:
                    r = Result(step, n, run_argv, "failed", rc=rc, secs=time.monotonic() - t0,
                               note="killed: its saved output passed the %d MB cap" % step.save_cap_mb)
                else:
                    r = Result(step, n, run_argv, "ok" if rc in step.ok_rc else "failed", rc=rc,
                               secs=time.monotonic() - t0)
                r.strays = strays
        stdout = _read_and_remove(out + ".stdout", cap)
        stderr = _read_and_remove(out + ".stderr", cap)
        if (step.unmapped_if and r.status in ("ok", "failed") and r.note is None
                and any(step.unmapped_if in b.decode("utf-8", errors="replace") for b in (stdout, stderr))):
            r.status, r.note = "unmapped", step.tool or os.path.basename(run_argv[0])
        self.save(r, out, stdout, stderr, cap)
        return r

    def save(self, r, out, stdout, stderr, cap=None):
        data = stdout
        if stderr:
            data += (b"" if not data or data.endswith(b"\n") else b"\n") + b"--- stderr ---\n" + stderr
        if cap is not None and len(data) > cap:
            data = data[:cap] + ("\n… saved output truncated at %d MB (save_cap_mb %d); the rest was not saved\n"
                                 % (r.step.save_cap_mb, r.step.save_cap_mb)).encode()
            r.truncated = True
        with open(out, "wb") as fh:
            fh.write(data)
        r.out, r.nbytes, r.sha = out, len(data), hashlib.sha256(data).hexdigest()
        r.stdout = stdout.decode("utf-8", errors="replace")
        r.text = data.decode("utf-8", errors="replace")

    def run(self, plan, setup=None):
        """Run the groups in ascending order, the steps of a group in parallel; SIGINT/TERM/HUP kill live steps.
        setup() runs first under the same handlers, so a signal during it is an Interrupted like any other."""
        handlers = {}

        def on_signal(signum, frame):
            raise Interrupted(signum)

        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            handlers[sig] = signal.signal(sig, on_signal)
        try:
            if setup is not None:
                setup()
            for group in sorted({step.group for step, invs, why in plan if invs is not None}):
                threads = [threading.Thread(target=self.run_step, args=(step, invs), daemon=True)
                           for step, invs, why in plan if invs is not None and step.group == group]
                self.threads += threads
                for t in threads:
                    t.start()
                for t in threads:
                    while t.is_alive():
                        t.join(0.2)
        except Interrupted:
            self.stop.set()
            with self.lock:
                procs = list(self.live)
            kill_groups(procs)
            for t in self.threads:
                t.join(10)
            raise
        finally:
            for sig, old in handlers.items():
                signal.signal(sig, old)


def _read_and_remove(path, limit=None):
    """The file's bytes (at most limit + 1 of them, so a cut can be seen), then the file is removed."""
    try:
        with open(path, "rb") as fh:
            data = fh.read() if limit is None else fh.read(limit + 1)
        os.unlink(path)
        return data
    except FileNotFoundError:
        return b""


def _signal_group(pgid, sig):
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError):
        pass


def _group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def kill_groups(procs, grace=KILL_GRACE_S):
    """SIGTERM to each process group, SIGKILL to the groups still alive `grace` seconds later, then reap. grace None:
    SIGKILL at once, no SIGTERM (a step past its save cap: during a grace a writer that ignores SIGTERM fills the disk,
    measured 120 MB past a 1 MB cap, VERIFY-LS-B9 F-7)."""
    pending = list(procs)
    if grace is not None:
        for p in procs:
            _signal_group(p.pid, signal.SIGTERM)
        deadline = time.monotonic() + grace
        while pending and time.monotonic() < deadline:
            for p in pending:
                p.poll()
            pending = [p for p in pending if _group_alive(p.pid)]
            if pending:
                time.sleep(0.05)
    for p in pending:
        _signal_group(p.pid, signal.SIGKILL)
    for p in procs:
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass


# ---------- output ----------

def cap_lines(text, cap, out):
    lines = text.split("\n")
    if len(lines) <= cap:
        return text
    head, tail = (cap + 1) // 2, cap // 2
    marker = "… %d lines cut (cap_lines %d); full output: %s" % (len(lines) - head - tail, cap, out)
    return "\n".join(lines[:head] + [marker] + (lines[len(lines) - tail:] if tail else []))


def cut_middle(body, keep, out):
    """The body cut to about `keep` characters, its head and its tail, at line ends where one is near."""
    head, tail = body[:keep // 2], body[len(body) - (keep - keep // 2):] if keep - keep // 2 else ""
    if "\n" in head:
        head = head[:head.rfind("\n")]
    if "\n" in tail:
        tail = tail[tail.find("\n") + 1:]
    marker = "… %d characters cut (the %s-character print cap); full output: %s" % (
        len(body) - len(head) - len(tail), format(PRINT_CAP, ","), out)
    return "\n".join(x for x in (head, marker, tail) if x)


def assemble(header, sections, cap=PRINT_CAP):
    """The print: header lines, then each section's head lines and body; over `cap` characters the largest bodies
    are cut first (one level L: every body longer than L keeps about L characters), and the header says which."""
    def render(bodies, cut):
        lines = list(header)
        if cut:
            lines.append("print capped at %s characters: shortened %s" % (format(cap, ","), ", ".join(cut)))
        for (name, head, _body, _out), body in zip(sections, bodies):
            lines += head + ([body] if body else [])
        return "\n".join(lines) + "\n"

    text = render([s[2] for s in sections], [])
    if len(text) <= cap:
        return text
    lo, hi, best = 0, max(len(s[2]) for s in sections), None
    while lo <= hi:
        level = (lo + hi) // 2
        bodies = [cut_middle(b, level, out) if len(b) > level else b for _n, _h, b, out in sections]
        attempt = render(bodies, [n for n, _h, b, _o in sections if len(b) > level])
        if len(attempt) <= cap:
            best, lo = attempt, level + 1
        else:
            hi = level - 1
    if best is None:
        marker = "\n… the print is cut at %s characters (the headers alone are over the cap)\n" % format(cap, ",")
        best = render([""] * len(sections), [s[0] for s in sections])[:cap - len(marker)] + marker
    return best


def status_text(r):
    step = r.step
    if r.status == "ok":
        s = "ok · rc %s · %.2f s" % (r.rc, r.secs)
    elif r.status == "failed":
        s = "FAILED · %s · %.2f s" % ("rc %s" % r.rc if r.rc is not None else r.note, r.secs)
        if r.rc is not None and r.note:
            s += " — " + r.note
    elif r.status == "timeout":
        s = "TIMEOUT after %d s" % step.timeout
    elif r.status == "unmapped":
        s = "unmapped — %s unavailable" % r.note
    else:
        s = "SKIPPED — %s" % r.note
    if r.strays:
        s += " · killed what it left running"
    return s + ("" if step.required or r.status == "ok" else " (not required)")


def fmt_value(v):
    return shlex.quote(",".join(v) if isinstance(v, list) else v)


# ---------- records ----------

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


def append_line(log_dir, obj):
    """One JSON line appended to runs.jsonl in ONE write, under flock of .lock; any failure -> Refusal(3)."""
    data = (json.dumps(obj, separators=(",", ":")) + "\n").encode()
    try:
        os.makedirs(log_dir, exist_ok=True)
        lock = os.open(os.path.join(log_dir, ".lock"), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX)
            fd = os.open(os.path.join(log_dir, "runs.jsonl"), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
            try:
                if os.write(fd, data) != len(data):
                    raise OSError("a short write to runs.jsonl")
            finally:
                os.close(fd)
        finally:
            os.close(lock)
    except OSError as e:
        raise Refusal(3, "log %s: %s" % (log_dir, e))


def check_ratings(ratings, log_dir, stacks):
    """Every rated run (and step) must have a record in runs.jsonl, of a stack declared rated = true: an unknown run,
    step or an unrated stack -> Refusal(2); an unreadable log -> Refusal(3)."""
    wanted = {r["run"] for r in ratings}
    steps, labels = {}, {}
    path = os.path.join(log_dir, "runs.jsonl")
    try:
        with open(path, "rb") as fh:
            for i, raw in enumerate(fh, 1):
                try:
                    rec = json.loads(raw)
                except ValueError:
                    raise Refusal(3, "log %s: line %d is not JSON" % (path, i))
                if isinstance(rec, dict) and rec.get("run") in wanted and "steps" in rec:
                    steps[rec["run"]] = {s.get("id") for s in rec["steps"]}
                    labels[rec["run"]] = rec.get("label")
    except FileNotFoundError:
        pass
    except OSError as e:
        raise Refusal(3, "log %s: %s" % (path, e))
    rated = sorted(label for label, st in stacks.items() if st.rated)
    for r in ratings:
        if r["run"] not in steps:
            raise Refusal(2, "rating: run %s has no record in %s" % (r["run"], path))
        stack = stacks.get(labels[r["run"]])
        if stack is None or not stack.rated:
            raise Refusal(2, "rating: run %s is a %s run, and only a rated stack takes ratings (%s)"
                          % (r["run"], labels[r["run"]], ", ".join(rated) or "none"))
        if r["step"] is not None and r["step"] not in steps[r["run"]]:
            raise Refusal(2, "rating: run %s has no step %s (its steps: %s)"
                          % (r["run"], r["step"], ", ".join(sorted(steps[r["run"]]))))


def rating_lines(ratings):
    ts = utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{"v": 1, "rating": r["run"] + ("." + r["step"] if r["step"] else ""), "rel": r["rel"], "use": r["use"],
             "ts": ts} for r in ratings]


# ---------- commands ----------

def list_lines(stack):
    """A stack's catalog lines: its label, parameters and summary, then its notes, indented."""
    parts = []
    for name in stack.settable():
        p = stack.params[name]
        shape = "|".join(p.choices) if p.type == "choice" else "<%s>" % p.type
        parts.append(("%s=%s" if p.required else "[%s=%s]") % (name, shape))
    return ["%s  %s  — %s%s" % (stack.label, " ".join(parts) or "(no parameters)", stack.summary,
                                " · rated" if stack.rated else "")] + ["  note: " + n for n in stack.notes]


def cmd_list(stacks):
    for stack in stacks.values():
        print("\n".join(list_lines(stack)))
    return 0


def catalog(registry):
    """The SessionStart text: a heading line, `list`'s lines, one line on ratings, under CATALOG_CAP characters (whole
    stacks dropped from the end, with a line saying so). Never raises: on any failure it is ONE line naming why."""
    try:
        _tools, stacks = load_registry(registry)
        head = ("Stacks (scripts/stacks.toml): `python3 scripts/stack.py <label> key=value ...` runs one in one call; "
                "`python3 scripts/stack.py explain <label> ...` prints its plan and runs nothing.")
        rate = ("Ratings, the content stacks only (%s): `--rate <run id>=<rel>/<use>` on the next stack call, or "
                "`python3 scripts/stack.py rate <run id>=<rel>/<use>`; rel and use are 0 to 3."
                % (", ".join(label for label, st in stacks.items() if st.rated) or "none"))
        blocks = [list_lines(st) for st in stacks.values()]
        shown, cut = len(blocks), []
        while True:
            text = "\n".join([head] + [ln for b in blocks[:shown] for ln in b] + cut + [rate]) + "\n"
            if len(text) < CATALOG_CAP or shown == 0:
                break
            shown -= 1
            cut = ["… %d of %d stacks not shown (this catalog stays under %s characters): python3 scripts/stack.py list"
                   % (len(blocks) - shown, len(blocks), format(CATALOG_CAP, ","))]
        return text if len(text) < CATALOG_CAP else text[:CATALOG_CAP - 3] + "…\n"
    except Exception as e:          # fail loud, never silent: the hook's reader learns why there is no catalog
        why = " ".join(("%s: %s" % (type(e).__name__, e) if not isinstance(e, Refusal) else str(e)).split())
        return "stacks: no catalog (%s)\n" % (why if len(why) <= 300 else why[:300] + "…")


def log_dir_of(opts, env):
    return os.path.realpath(opts.log_dir) if opts.log_dir else os.path.join(env.get("main"), ".jev", "stacks")


def cmd_explain(stack, tokens, tools, opts):
    tree = resolve_tree(opts.tree)
    env = Env(tree, opts, stack, {})
    env.values = parse_tokens(stack, tokens, tree, env)
    env.run, env.tmp = "<run>", "<tmp>"
    plan = build_plan(stack, env.values, env)
    head = env.head_or_none()
    lines = ["explain %s — %s" % (stack.label, stack.summary),
             "tree %s · HEAD %s" % (tree, head[:12] if head else "none"),
             "params: %s" % (" ".join("%s=%s" % (k, fmt_value(v)) for k, v in env.values.items()) or "(none)"),
             "<run> = %s/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>" % log_dir_of(opts, env)]
    if env.tmp_used:
        lines.append("<tmp> = %s/stack-<run id>, outside every git work tree; removed after the run" % TMP_BASE)
    for group in stack.groups:
        lines.append("group %d" % group)
        for step, invs, why in plan:
            if step.group != group:
                continue
            if invs is None:
                lines.append("  %s: not selected (%s)" % (step.id, why))
                continue
            notes = []
            if len(invs) > 1 and step.foreach is None:
                notes.append("×%d" % len(invs))
            if step.timeout != 60:
                notes.append("timeout %d s" % step.timeout)
            if step.ok_rc != (0,):
                notes.append("ok_rc %s" % ",".join(map(str, step.ok_rc)))
            if not step.required:
                notes.append("optional")
            if step.foreach_chain is not None:
                notes.append("one call per line of %s" % step.foreach_chain)
            if step.needs:
                notes.append("needs %s" % ", ".join(step.needs))
            if step.empty_ok:
                notes.append("nothing to do when its input is empty")
            if step.headline:
                notes.append("headline")
            suffix = " (%s)" % ", ".join(notes) if notes else ""
            if step.foreach is not None:
                for n, _each, parts in invs:
                    lines.append("  %s [%d/%d]: %s%s" % (step.id, n, len(invs), display(parts), suffix))
            else:
                lines.append("  %s: %s%s" % (step.id, display(invs[0][2]), suffix))
    print("\n".join(lines))
    return 0


def make_tmp(path, made):
    """{tmp}: a fresh 0700 dir that no git work tree holds, added to `made` as soon as it exists (the caller removes
    what `made` holds, whatever happens next); any failure -> Refusal(3)."""
    try:
        os.mkdir(path, 0o700)
    except OSError as e:
        raise Refusal(3, "{tmp} %s: %s" % (path, e))
    made.append(path)
    if git_out(path, "rev-parse", "--show-toplevel") is not None:
        raise Refusal(3, "{tmp} %s lies inside a git work tree; it must lie outside every one" % path)


def remove_tmp(path):
    """The header's line on {tmp}: removed, or not (and why)."""
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    except OSError as e:
        return "tmp %s · NOT removed: %s" % (path, e)
    return "tmp %s · removed after the run" % path


def cmd_run(stack, tokens, tools, opts, stacks):
    tree = resolve_tree(opts.tree)
    env = Env(tree, opts, stack, {})
    env.values = values = parse_tokens(stack, tokens, tree, env)
    now = utc_now()
    run_id = "s-%s-%s" % (now.strftime("%Y%m%dT%H%M%SZ"), secrets.token_hex(3))
    log_dir = log_dir_of(opts, env)
    env.run = run_dir = os.path.join(log_dir, run_id)
    env.tmp = os.path.join(TMP_BASE, "stack-" + run_id)
    plan = build_plan(stack, values, env)
    ratings = parse_ratings(opts.rate)
    if ratings:
        check_ratings(ratings, log_dir, stacks)
    head = env.head_or_none()
    try:
        os.makedirs(log_dir, exist_ok=True)
        os.mkdir(run_dir)
    except OSError as e:
        raise Refusal(3, "log %s: %s" % (log_dir, e))
    runner = Runner(tree, run_dir, tools)
    made = []

    def setup():                # under the runner's signal handlers, like the steps
        if env.tmp_used:
            make_tmp(env.tmp, made)
        for line in rating_lines(ratings):
            append_line(log_dir, line)

    try:                        # {tmp} is removed on success, failure and signal alike (a SIGKILL cannot)
        runner.run(plan, setup)
    finally:
        tmp_line = remove_tmp(made[0]) if made else None
    results = [r for step, invs, why in plan if invs is not None for r in runner.results.get(step.id, [])]
    bad = [r for r in results if r.step.required and r.status != "ok"]
    rc = 1 if bad else 0
    record = {"v": 1, "run": run_id, "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "label": stack.label, "params": values,
              "tree": tree, "head": head, "rc": rc, "steps": []}
    for r in results:
        s = {"id": r.step.id}
        if r.n is not None:
            s["n"] = r.n
        s.update({"argv": r.argv, "rc": r.rc, "status": r.status, "secs": round(r.secs, 3), "bytes": r.nbytes,
                  "sha256": r.sha, "out": r.out})
        if r.truncated:
            s["truncated"] = True
        if r.strays:
            s["strays_killed"] = True
        record["steps"].append(s)
    log_error = None
    try:
        append_line(log_dir, record)
    except Refusal as e:
        log_error = e
    header = ["stack %s · run %s · exit %d%s" % (stack.label, run_id, rc if log_error is None else 3,
                                                 "" if not bad else " — required, not ok: " + ", ".join(
                                                     sorted({r.step.id for r in bad}))),
              "tree %s · HEAD %s" % (tree, head[:12] if head else "none")]
    # A headline step's first stdout line, before params: over the print cap the header is cut from its end, and a
    # long paths= value made params the line that pushed the gate's counts out of the print (VERIFY-LS-B9 R3-F1). Its
    # control characters are escaped first (R3-F5), then it is cut: the header line stays bounded.
    for step, invs, why in plan:
        first = next((ln for r in runner.results.get(step.id, []) for ln in r.stdout.split("\n") if ln.strip()), None)
        if step.headline and first is not None:
            first = CONTROL_RE.sub(lambda m: repr(m.group())[1:-1], first)
            header.append("%s · %s" % (step.id, first if len(first) <= HEADLINE_MAX else first[:HEADLINE_MAX] + "…"))
    header += ["params: %s" % (" ".join("%s=%s" % (k, fmt_value(v)) for k, v in values.items()) or "(none)"),
               "outputs: %s/ (<step>.out each) · record: %s" % (run_dir, os.path.join(log_dir, "runs.jsonl"))]
    if tmp_line:
        header.append(tmp_line)
    skipped = ["%s (%s)" % (step.id, why if invs is None else runner.idle[step.id]) for step, invs, why in plan
               if invs is None or step.id in runner.idle]
    if skipped:
        header.append("not selected: " + ", ".join(skipped))
    sections = []
    for r in results:
        name = r.step.id + ("" if r.n is None else "[%d/%d]" % (r.n, len(runner.results[r.step.id])))
        head_lines = ["", "## %s · %s" % (name, status_text(r)), "$ " + display(r.argv)]
        quiet = r.status == "skipped" or (r.status == "unmapped" and r.rc is None)   # the head line says it all
        body = "" if quiet else cap_lines(r.text.rstrip("\n"), r.step.cap_lines, r.out)
        sections.append((name, head_lines, body, r.out))
    sys.stdout.write(assemble(header, sections))
    sys.stdout.flush()
    if log_error is not None:
        raise log_error
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(prog="stack.py", allow_abbrev=False, description=__doc__.splitlines()[0])
    ap.add_argument("--tree", help="the target tree, a git toplevel (default: the toplevel of the current directory)")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY, help=argparse.SUPPRESS)
    ap.add_argument("--log-dir", help=argparse.SUPPRESS)
    ap.add_argument("--transcript-root", default=DEFAULT_TRANSCRIPT_ROOT, help=argparse.SUPPRESS)
    ap.add_argument("--rate", action="append", default=[], metavar="RUN[.STEP]=REL/USE")
    ap.add_argument("command", help="list | catalog | explain | rate | a stack label")
    ap.add_argument("tokens", nargs="*", help="key=value parameters (explain: the label first; rate: ratings)")
    opts = ap.parse_intermixed_args(argv)
    if opts.command == "catalog":   # the SessionStart hook's text: exit 0 always, a failure is one line on stdout
        sys.stdout.write(catalog(opts.registry) if not (opts.tokens or opts.rate) else
                         "stacks: no catalog (catalog takes no argument)\n")
        return 0
    try:
        tools, stacks = load_registry(opts.registry)
        if opts.command == "list":
            if opts.tokens or opts.rate:
                raise Refusal(2, "list takes no argument")
            return cmd_list(stacks)
        if opts.command == "rate":
            ratings = parse_ratings(opts.tokens + opts.rate)
            if not ratings:
                raise Refusal(2, "rate needs at least one RUN[.STEP]=REL/USE")
            if opts.log_dir:
                log_dir = os.path.realpath(opts.log_dir)
            else:
                log_dir = os.path.join(Env(resolve_tree(opts.tree), opts, None, {}).get("main"), ".jev", "stacks")
            check_ratings(ratings, log_dir, stacks)
            for line in rating_lines(ratings):
                append_line(log_dir, line)
            print("rated: %s" % ", ".join("%s=%d/%d" % (x["rating"], x["rel"], x["use"]) for x in rating_lines(ratings)))
            return 0
        explain = opts.command == "explain"
        tokens = list(opts.tokens)
        if explain:
            if opts.rate:
                raise Refusal(2, "explain writes no record: --rate rides on a run or on `rate`")
            if not tokens:
                raise Refusal(2, "explain needs a stack label; known labels: %s" % ", ".join(stacks))
            label = tokens.pop(0)
        else:
            label = opts.command
        if label not in stacks:
            raise Refusal(2, "unknown stack %r; known labels: %s" % (label, ", ".join(stacks)))
        if explain:
            return cmd_explain(stacks[label], tokens, tools, opts)
        return cmd_run(stacks[label], tokens, tools, opts, stacks)
    except Refusal as e:
        sys.stderr.write("stack: %s\n" % e)
        return e.code
    except Interrupted as e:
        sys.stderr.write("stack: interrupted by signal %d; the live steps were killed, no record written\n" % e.signum)
        return 128 + e.signum


if __name__ == "__main__":
    sys.exit(main())
