#!/usr/bin/env python3
"""system1-context.py — the System-1 context layer, parts L1 and L3 (D-090; S1-L1, repaired by S1-L1-R1; the prompt
path reads every skill since S1-ALL, D-093).

Design: docs/research/findings/system1-context/DESIGN-2026-09-25.md, sections L1 and L3. A rule that says "load skill X
before Y" does not load the skill (AF-AP-218: 12 Skill calls in the main transcripts, while the hooks that inject fired
hundreds of times). So this hook injects the governing skill text itself, verbatim, before the agent acts:

  PreToolUse (Write, Edit, Bash)   L1. The tool input (the file path, the written text, the command) is matched against
                                   the situation table, system1-situations.json beside this file. Each matching row's
                                   key entries are injected verbatim from its skill section, then one line
                                   `full details: <skill file> § <heading>`. A command row sees shell code only:
                                   quoted text, heredoc bodies and comments are data unless a shell reads them.
  UserPromptSubmit                 L3. The prompt is keyword-matched against the SECTIONS (a skill split at its
                                   headings) of every skill under .claude/skills: a skill's description and name say
                                   what it is for, its headings and body which section. A library skill (not in the
                                   table's project_skills) counts only when the prompt names it, and its excerpt starts
                                   with its one-line description. The best one or two excerpts are injected, each with
                                   its pointer. It runs beside wiki-context.py, never inside it.
  --reset (from session-start.sh)  SessionStart `compact`, `resume` or `clear`: the window's marker is removed.

Once per context window: the key of every injected line goes into a marker, <state>/system1-seen/<session>.<agent>.json
(`agent` is the payload's `agent_id`, present only inside a subagent, which is its own window, else `main`). A line
already in the marker is not injected again; a row whose lines were all injected is skipped as a duplicate. A lock on
the marker serializes the calls of one window; a call that cannot take it in time injects nothing.

Budget: at most 2,048 bytes per tool call and 4,096 per prompt. A row's text goes in whole skill entries: an entry that
does not fit waits for the next matching call in the window, it is never cut inside. A prompt excerpt is cut at a line
boundary, and when not even its first line fits, its label and pointer still go. Every block keeps its pointer. The
text is plain: the registration runs this hook through scripts/hook_context.py, which hands it to the model as
additionalContext (plain PreToolUse stdout reaches only the transcript view, AF-AP-172).

Advisory, never a gate: every path exits 0 and nothing blocks. Off switch: the file <state>/system1-off (the reset
still runs, so a marker never outlives its window). Telemetry: one JSON line per decision in <state>/system1.jsonl
(time, event, tool, the situations matched, the keys injected or skipped and why, the bytes); ids, keys and counts only,
never the tool input or the prompt. A prompt excerpt's entry also carries its skill, heading, score, whether the skill
is a project skill, and the sha256 of the excerpt's text: the transcript records that text, so the agent's scores of an
injection (task #295) join its entry on it. An exception injects nothing and logs its type (and its window, once
known); a row whose pattern or skill file fails is skipped alone, with its type.

Latency: no instrument, no network, no model. The prompt path reads its index of every skill through
<state>/system1-cache.json, rebuilt whole only when a SKILL.md is added, removed or changed (its mtime or size); the
tool path parses only the one to three skill files a call needs, which costs less than loading that index.
Measured on the 413-skill tree (S1-ALL report): the index builds in about 0.6 s, once per change of the tree; warm,
a prompt plans in 23 ms at the median and 36 ms at p95, and the whole hook process takes 64 and 90 ms (the PIN's: 38
and 50).

<state> is <repo>/.jev. Test seam, read once at start: AF_SYSTEM1_STATE (the state directory instead of <repo>/.jev).
"""
import json
import os
import re
import sys
import time

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HOOK_DIR))
TABLE_PATH = os.path.join(HOOK_DIR, "system1-situations.json")
SKILLS_DIR = os.path.join(ROOT, ".claude", "skills")

TOOL_BUDGET = 2048
PROMPT_BUDGET = 4096
PROMPT_EXCERPTS = 2                  # the best one or two sections per prompt, each at most PROMPT_BUDGET // 2
PROMPT_SCAN_CHARS = 4000             # a pasted document is matched on its head
MIN_PROMPT_SCORE = 70.0             # a project section with two or more lead words (noise is worse than absence)
ONE_LEAD_MIN_SCORE = 80.0           # a project section with ONE lead word (F5)
SHORT_MIN_SCORE = 30.0              # ... with two or more, in a short prompt: this, when they carry MIN_COVER
MIN_COVER = 0.2                     # the share of the prompt's weight (skill-level idf) its lead words carry
NAMED_MIN_SCORE = 40.0              # a section of a skill the prompt names: the only way a library skill counts
SECOND_EXCERPT_RATIO = 0.75          # a second section only when it scores at least this share of the best one
LEAD_MIN_IDF = 2.0                   # a lead word: at most one skill in e^2 - 1 (6.4) holds it
BODY_K1, BODY_B = 1.2, 0.75          # BM25's defaults: a long section's body counts for less
DESCRIPTION_MAX = 300                # bytes of a library skill's description line
INDEX_VERSION = 2                    # the prompt index's format in <state>/system1-cache.json
TOOLS = ("Write", "Edit", "Bash")
STDIN_WAIT_S = 2.0
LOCK_WAIT_S = 0.5
LOG_MAX_BYTES = 4_000_000            # then system1.jsonl moves to system1.jsonl.1
MARKER_MAX_AGE_S = 7 * 86400         # the reset also prunes markers of long-gone sessions

# Harness events are not a person's prompt: the same prefixes as wiki-context.py (a test pins the equality).
HARNESS_EVENT_PREFIXES = ("[SYSTEM NOTIFICATION", "Another Claude session sent a message", "Stop hook feedback",
                          "<task-notification>", "<agent-message")
STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "it",
    "that", "this", "with", "you", "we", "i", "me", "my", "our", "your", "do",
    "does", "can", "how", "what", "why", "just", "like", "yeah", "um", "uh",
    "also", "know", "now", "get", "go", "be", "have", "was", "are", "at",
    "not", "but", "all", "any", "one", "use", "from", "has", "had", "its", "let", "lets", "will", "would", "should",
    "could", "then", "than", "them", "they", "there", "their", "here", "when", "which", "who", "into", "out", "about",
    "please", "okay", "yes", "did", "done", "need", "want", "see", "look", "make", "sure", "way", "more", "some",
    # S1-ALL: the corpus is documentation, where the words of speech are rare, so rarity alone would make them leads;
    # and URL parts, which a description's link spreads over unrelated prompts.
    "again", "ago", "ahead", "already", "although", "always", "another", "anything", "anyway", "anywhere", "around",
    "away", "back", "basically", "been", "before", "being", "best", "better", "between", "both", "came", "come",
    "comes", "coming", "cool", "definitely", "didn", "don", "doesn", "doing", "down", "each", "either", "else",
    "enough", "especially", "etc", "even", "ever", "every", "everything", "exactly", "far", "few", "fine", "first",
    "found", "gave", "getting", "give", "given", "gives", "giving", "going", "gone", "gonna", "good", "got", "gotta",
    "great", "guess", "guy", "guys", "hey", "hmm", "honestly", "isn", "keep", "kind", "last", "later", "least", "less",
    "lot", "lots", "maybe", "mean", "means", "might", "mine", "most", "much", "must", "myself", "never", "next", "nice",
    "nothing", "off", "often", "once", "only", "other", "others", "over", "own", "part", "per", "perhaps", "pretty",
    "probably", "put", "quite", "rather", "really", "right", "said", "same", "saw", "say", "saying", "says", "seem",
    "seems", "since", "something", "sometimes", "somewhere", "soon", "sort", "still", "stuff", "such", "take", "taken",
    "takes", "taking", "tell", "thank", "thanks", "thing", "things", "think", "thinking", "those", "though", "thought",
    "through", "till", "today", "together", "told", "too", "took", "tried", "tries", "try", "trying", "under", "until",
    "upon", "very", "via", "wanna", "wasn", "well", "went", "were", "whatever", "whether", "while", "whole", "whose",
    "within", "without", "won", "wouldn", "yet", "yours", "aren", "weren", "haven", "hasn", "hadn", "couldn", "shouldn",
    "mustn", "yep", "nope", "huh", "umm", "uhh", "wow", "lol", "long", "time", "times",
    "http", "https", "www", "com", "org", "github", "html",
}

HEADING_RX = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOKEN_RX = re.compile(r"[a-z0-9_]{3,}")
FRONT_RX = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*$", re.S | re.M)       # a SKILL.md's frontmatter block
DQ_ESCAPES = {"n": " ", "t": " ", "\\": "\\", '"': '"', "/": "/", "0": "", " ": " "}   # YAML double-quoted, folded
# A line that starts a new entry: a heading, a bold lead, a list item, a numbered or lettered item, a table, a quote, a
# fence. Other non-blank lines continue the entry above them.
ENTRY_START_RX = re.compile(r"^\s*(?:\*\*|#{1,6}\s|[-*+]\s|\d+[a-z]?\.\s|\([a-z0-9]{1,3}\)\s|\||>|```)")
# A command position in shell code (see shell_code for what is code): the start, after a separator or a keyword
# (`while`, `if`, `!`, `{` and the like start a command too, F1), past variable assignments, an interpreter and a
# directory prefix, so `cd x && FOO=1 bash /abs/scripts/pc.sh` puts `pc.sh` at a command position. A row's `command`
# pattern is matched AT these positions, so it names the command word without a directory (the table test holds
# that). A word here is `[^\s;&|()`]`: no part of the scan runs past the next separator, so it is linear on any input
# (F7: the old `\S*/` rescanned the rest of a run from every separator). Compiling this prefix once instead of into
# every row's pattern took the table load from 8.1 to 2.5 ms (measured).
_W = r"[^\s;&|()`]"
CMD_POS = (r"(?:^|[;&|(\n`]|\$\(|(?<![^\s;&|(`])[!{]\s|\b(?:then|do|else|while|until|if|elif|nohup|setsid|exec|time|"
           r"sudo|env|xargs|timeout\s+\S+)\s)\s*(?:[A-Za-z_][A-Za-z0-9_]*=" + _W + r"*\s+)*"
           r"(?:(?:bash|sh|python3?|node|npx|bunx|pnpm\s+dlx|uv\s+run)\s+(?:-" + _W + r"+\s+)*)?(?:" + _W + r"*/)?")
DETECTORS = ("command", "command_any", "path", "path_not", "text")

# Who reads quoted text or a heredoc as shell code (F6). `python3 - <<'PY'`, `git commit -m '…'` and `grep 'x'` hand
# theirs to a program as data.
SHELLS = ("bash", "sh", "zsh", "dash", "ksh")
QUOTE_READERS = ("ssh", "pc.sh", "eval")        # every quoted word after these is a nested shell's command line
C_FLAG_RX = re.compile(r"-[A-Za-z]*c[A-Za-z]*\Z")  # `bash -c`, `sh -lc`: the quoted word after it is a script
HEREDOC_RX = re.compile(r"<<(-?)[ \t]*(?:'([^'\n]*)'|\"([^\"\n]*)\"|(\\?)([A-Za-z0-9_.+-]+))")
RUN_RX = re.compile(r"[^\\'\"`$#<\s]+")             # word characters and separators: what the code scan takes in bulk
DQ_STOP_RX = re.compile(r"[\\\"`$]")
DOC_STOP_RX = re.compile(r"[\\`$]")
MAX_NEST = 16


# ---------------------------------------------------------------- input

def read_stdin(wait_s=STDIN_WAIT_S):
    """The hook payload. Bounded: a terminal, or a pipe or socket that stays open with nothing on it, reads as empty."""
    import select
    try:
        fd = sys.stdin.fileno()
    except (AttributeError, ValueError, OSError):
        return b""
    if os.isatty(fd):
        return b""
    chunks, deadline = [], time.monotonic() + wait_s
    while True:
        left = deadline - time.monotonic()
        if left <= 0 or not select.select([fd], [], [], left)[0]:
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def load_table(path=TABLE_PATH):
    return json.loads(read_regular(path, follow=True).decode("utf-8"))


def detectors(row):
    """The row's compiled detectors, compiled on first use (a call compiles only the rows its tool can match)."""
    rx = row.get("_rx")
    if rx is None:
        rx = row["_rx"] = {k: re.compile(row[k]) if row.get(k) else None for k in DETECTORS}
    return rx


def command_positions(cmd):
    """Every offset of `cmd` where a command word starts: after a separator, its assignments, an interpreter and a
    directory prefix."""
    return sorted({m.end() for m in re.finditer(CMD_POS, cmd)})


def _mask(edits, a, b, ch="x"):
    if b > a:
        edits.append((a, b, ch))


def _word(reads, w):
    """Update who reads the next quote or heredoc of this simple command: [quote read by a shell, a shell word seen,
    only options since it, ssh seen]."""
    base = w.rsplit("/", 1)[-1]
    if base in QUOTE_READERS:
        reads[0] = True
        reads[3] = reads[3] or base == "ssh"
    elif base in SHELLS:
        reads[1], reads[2] = True, True
    elif reads[1]:
        reads[0] = reads[0] or bool(C_FLAG_RX.match(w))
        reads[2] = reads[2] and w.startswith("-")


def _code(cmd, i, hi, edits, closer, nest):
    """Scan shell code in cmd[i:hi] up to `closer` (")" of a `$(`, a backtick, the '"' of a quote a shell reads, or
    None for hi). Appends the data spans to `edits`, left to right; returns the closer's index (hi when absent)."""
    reads, ws, depth, docs = [False, False, True, False], None, 0, []
    while i < hi:
        run = RUN_RX.match(cmd, i, hi)                   # word characters and separators, taken in bulk
        if run:
            k = run.end()
            if closer == ")":                            # a paren inside `$(`: counted one at a time below
                k = min([p for p in (cmd.find("(", i, k), cmd.find(")", i, k)) if p >= 0] or [k])
            if k > i:
                last = max(cmd.rfind(s, i, k) for s in ";&|()")
                if last >= 0:                            # a separator: a new command, its word after it
                    reads[:] = [False, False, True, False]
                    ws = last + 1 if last + 1 < k else None
                elif ws is None:
                    ws = i
                i = k
                continue
        j = i
        c = cmd[j]
        if c == closer and (c != ")" or depth == 0):
            return j
        continuation = c == "\\" and cmd.startswith("\\\n", j)
        if c.isspace() or c in ";&|()<" or continuation:
            if ws is not None:
                _word(reads, cmd[ws:j])
                ws = None
            if continuation:                                     # `\` + newline joins two lines: a space, not a newline
                _mask(edits, j, j + 2, " ")
                i = j + 2
                continue
            if c == "<":
                doc = HEREDOC_RX.match(cmd, j, hi) if cmd.startswith("<<", j) and not cmd.startswith("<<<", j) else None
                if doc:
                    quoted = doc.group(5) is None or doc.group(4) == "\\"
                    delim = next(g for g in (doc.group(2), doc.group(3), doc.group(5)) if g is not None)
                    docs.append((delim, doc.group(1) == "-", reads[3] or (reads[1] and reads[2]), not quoted))
                    i = doc.end()
                else:
                    i = j + (3 if cmd.startswith("<<<", j) else 1)
                continue
            if c != " " and c != "\t":
                reads[:] = [False, False, True, False]         # a separator or a newline starts a new command
                depth += (c == "(") - (c == ")")
            i = j + 1
            if c == "\n" and docs:
                for doc in docs:
                    i = _heredoc(cmd, i, hi, edits, doc, nest)
                docs = []
            continue
        if ws is None:
            ws = j
        if c == "\\":                                       # an escaped character is never a separator or a quote
            _mask(edits, j + 1, min(j + 2, hi))
            i = j + 2
        elif c == "'":
            k = cmd.find("'", j + 1, hi)
            k = hi if k < 0 else k
            if reads[0] and nest < MAX_NEST:
                edits.append((j, j + 1, ";"))                  # a shell's script: its first word is a command
                _code(cmd, j + 1, k, edits, None, nest + 1)
            else:
                _mask(edits, j + 1, k)
            i = k + 1
        elif c == '"':
            if reads[0] and nest < MAX_NEST:
                edits.append((j, j + 1, ";"))
                i = _code(cmd, j + 1, hi, edits, '"', nest + 1) + 1
            else:
                i = _dquote(cmd, j + 1, hi, edits, nest)
        elif c == "`" or (c == "$" and cmd.startswith("$(", j)):
            k = j + (1 if c == "`" else 2)
            i = (_code(cmd, k, hi, edits, "`" if c == "`" else ")", nest + 1) + 1) if nest < MAX_NEST else k
        elif c == "#" and ws == j:                           # `#` starting a word: a comment to the end of the line
            k = cmd.find("\n", j, hi)
            k = hi if k < 0 else k
            _mask(edits, j, k)
            ws, i = None, k
        else:
            i = j + 1
    return hi


def _dquote(cmd, i, hi, edits, nest):
    """A double-quoted string no shell reads, from i (after its opening quote): data, except a `$(…)` or backtick
    substitution, which the shell runs. Returns the index after its closing quote."""
    while i < hi:
        m = DQ_STOP_RX.search(cmd, i, hi)
        if m is None:
            break
        j = m.start()
        c = cmd[j]
        if c == '"':
            _mask(edits, i, j)
            return j + 1
        if c == "\\":
            _mask(edits, i, min(j + 2, hi))
            i = j + 2
        elif nest < MAX_NEST and (c == "`" or cmd.startswith("$(", j)):
            _mask(edits, i, j)
            k = j + (1 if c == "`" else 2)
            i = _code(cmd, k, hi, edits, "`" if c == "`" else ")", nest + 1) + 1
        else:
            _mask(edits, i, j + 1)
            i = j + 1
    _mask(edits, i, hi)
    return hi


def _heredoc(cmd, i, hi, edits, doc, nest):
    """One heredoc body, from i (the line after its `<<` line) to its terminator line: a shell's code when a shell reads
    it, else data (a `$(…)` or backtick in it stays code when the delimiter is unquoted). The body's last newline is
    kept, so the terminator stays a line of its own. Returns the index after the terminator line."""
    delim, strip, shell, expands = doc
    start, body_end, nxt = i, hi, hi
    while i < hi:
        k = cmd.find("\n", i, hi)
        end = hi if k < 0 else k
        t = i
        while strip and t < end and cmd[t] == "\t":
            t += 1
        if end - t == len(delim) and cmd.startswith(delim, t):
            body_end, nxt = i, min(end + 1, hi)
            break
        i = end + 1
    if shell and nest < MAX_NEST:
        _code(cmd, start, body_end, edits, None, nest + 1)
        return nxt
    last = body_end - 1 if body_end > start and cmd[body_end - 1] == "\n" else body_end
    i = start
    while expands and i < last:
        m = DOC_STOP_RX.search(cmd, i, last)
        if m is None:
            break
        j = m.start()
        c = cmd[j]
        if c == "\\":
            _mask(edits, i, min(j + 2, last))
            i = j + 2
        elif nest < MAX_NEST and (c == "`" or cmd.startswith("$(", j)):
            _mask(edits, i, j)
            k = j + (1 if c == "`" else 2)
            i = _code(cmd, k, last, edits, "`" if c == "`" else ")", nest + 1) + 1
        else:
            _mask(edits, i, j + 1)
            i = j + 1
    _mask(edits, i, last)
    return nxt


def shell_code(cmd):
    """`cmd` with every character a shell does not run as code replaced by "x", same length, so an offset in it is an
    offset in `cmd` (F6). Data: single- and double-quoted text, heredoc bodies, comments. Code a nested shell reads stays
    code: a quoted word after `bash -c`, `sh -lc`, `ssh`, `pc.sh` or `eval` (its opening quote becomes ";", so its
    first word is a command), a heredoc fed to `bash` or `sh` with options only or to `ssh`, and a `$(…)` or backtick
    inside double quotes or an unquoted heredoc. One left-to-right pass that never scans a character twice (F7)."""
    edits = []
    _code(cmd, 0, len(cmd), edits, None, 0)
    out, pos = [], 0
    for a, b, ch in edits:
        out += [cmd[pos:a], ch * (b - a)]
        pos = b
    out.append(cmd[pos:])
    return "".join(out)


def rel_path(path, cwd):
    if not isinstance(path, str) or not path:
        return ""
    if not os.path.isabs(path):
        path = os.path.join(cwd if isinstance(cwd, str) and cwd else os.getcwd(), path)
    path = os.path.normpath(path)
    return path[len(ROOT) + 1:] if path.startswith(ROOT + os.sep) else path


def tool_fields(tool, ti, cwd):
    """(repo-relative path, written text, command) of one Write, Edit or Bash input."""
    if tool == "Bash":
        cmd = ti.get("command")
        cmd = cmd if isinstance(cmd, str) else ""
        return "", cmd, cmd
    text = ti.get("content") if tool == "Write" else ti.get("new_string")
    return rel_path(ti.get("file_path"), cwd), text if isinstance(text, str) else "", ""


def error_name(exc):
    """An exception's type as logged: module-qualified unless built in (`re.error`, not a bare `error`: F16)."""
    t = type(exc)
    mod = getattr(t, "__module__", "") or ""
    return t.__name__ if mod in ("builtins", "__main__") else f"{mod}.{t.__name__}"


# ---------------------------------------------------------------- skills

def parse_skill(text):
    """(lines, sections): a section is [heading, start, end) from its heading line to the next heading of any level.
    A '#' line inside a fenced block is not a heading."""
    lines = text.split("\n")
    heads, fence = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            m = HEADING_RX.match(line)
            if m:
                heads.append((m.group(2), i))
    sections = [(h, s, heads[k + 1][1] if k + 1 < len(heads) else len(lines)) for k, (h, s) in enumerate(heads)]
    return lines, sections


def skill_file(skill):
    return os.path.join(SKILLS_DIR, skill, "SKILL.md")


def read_skill(skill):
    return read_regular(skill_file(skill), follow=True).decode("utf-8")


def skill_pointer(skill, heading):
    return f"full details: .claude/skills/{skill}/SKILL.md § {heading}"


def line_key(skill, line):
    import hashlib
    return hashlib.sha1(f"{skill}\n{line}".encode("utf-8")).hexdigest()[:16]


def resolve(row, lines, sections):
    """The row's line indexes inside its section, in the row's order. LookupError when the heading or a selector does not
    resolve exactly (the skill changed under the table)."""
    spans = [(s, e) for h, s, e in sections if h == row["heading"]]
    if len(spans) != 1:
        raise LookupError(f"heading found {len(spans)} times")
    s, e = spans[0]
    out = []
    for sel in row["lines"]:
        start, to = (sel, None) if isinstance(sel, str) else (sel[0], sel[1])
        hits = [i for i in range(s + 1, e) if start in lines[i]]
        if len(hits) != 1:
            raise LookupError(f"selector found {len(hits)} times")
        i = hits[0]
        if to is None:
            j = i
            while j + 1 < e and lines[j + 1].strip() and not ENTRY_START_RX.match(lines[j + 1]):
                j += 1
        else:
            ends = [k for k in range(i, e) if to in lines[k]]
            if not ends:
                raise LookupError("selector end not found")
            j = ends[0]
        out.extend(k for k in range(i, j + 1) if k not in out)
    return out


def entry_units(idx, lines):
    """The row's lines as whole entries, the unit a call takes or leaves: a new unit at a gap, after a blank line and at
    a line that starts an entry. Blank lines are not injected."""
    units, prev = [], None
    for i in idx:
        if not lines[i].strip():
            prev = None
            continue
        if prev is None or i != prev + 1 or ENTRY_START_RX.match(lines[i]):
            units.append([])
        units[-1].append((i, lines[i]))
        prev = i
    return units


# ---------------------------------------------------------------- composing an injection

def compose(blocks, seen, budget, pointer_only=False):
    """blocks: [(row id, skill, heading, units, label)] in priority order, a unit being [(line index, line)] that goes
    in whole or waits for a later call (a whole entry on the tool path, one line on the prompt path). Lines in `seen`
    are left out; every block keeps its pointer. With `pointer_only`, a block none of whose lines fits still sends its
    label and pointer, once per window (F4). Returns (text, injected, skipped, new keys); `seen` is not changed."""
    out, used, injected, skipped, new = [], 0, [], [], []
    taken = set(seen)
    for rid, skill, heading, units, label in blocks:
        key = f"{skill} § {heading}"
        units = [u for u in ([(i, ln) for i, ln in u if ln.strip() and line_key(skill, ln) not in taken] for u in units) if u]
        if not units:
            skipped.append({"row": rid, "key": key, "why": "duplicate"})
            continue
        head, tail = label, skill_pointer(skill, heading)
        room = budget - used - len(head.encode()) - len(tail.encode()) - 2
        body, prev, n = [], None, 0
        for unit in units:
            part, need, p = [], 0, prev
            for i, ln in unit:
                gap = p is not None and i != p + 1
                cost = len(ln.encode()) + 1 + (4 if gap else 0)          # "…" plus its newline marks a gap
                part += ["…", ln] if gap else [ln]
                need += cost
                p = i
            if need > room:
                break                                                    # this entry waits, whole, for a later call
            body += part
            room -= need
            prev, n = p, n + len(unit)
        fresh = sum(len(u) for u in units)
        if not n:
            pkey = line_key(skill, tail)
            if not (pointer_only and room >= 0 and pkey not in taken):
                skipped.append({"row": rid, "key": key, "why": "duplicate" if pointer_only and pkey in taken else "budget"})
                continue
            new.append(pkey)                                             # the pointer alone, once per window
            taken.add(pkey)
        block = [head] + body + [tail]
        out.extend(block)
        size = sum(len(x.encode()) + 1 for x in block)
        used += size
        keys = [line_key(skill, ln) for ln in body if ln != "…"]
        taken.update(keys)
        new.extend(keys)
        rec = {"row": rid, "key": key, "lines": n, "bytes": size}
        if n < fresh:
            rec["cut"] = fresh - n                                       # left for a later call in this window
        injected.append(rec)
    text = "\n".join(out)
    return text, injected, skipped, new


def match_rows(table, tool, ti, cwd, skipped=None):
    """The rows whose detectors all match. A row whose pattern does not compile is left out alone, and noted in
    `skipped` (F16)."""
    path, text, cmd = tool_fields(tool, ti, cwd)
    code = shell_code(cmd) if cmd else ""                             # F6: what a shell runs, data masked
    hits, positions = [], None
    for row in table["rows"]:
        if tool not in row["tools"]:
            continue
        try:
            rx = detectors(row)
        except re.error as exc:
            if skipped is not None:
                skipped.append({"row": row.get("id"), "key": f"{row.get('skill')} § {row.get('heading')}",
                                "why": "error", "error": error_name(exc)})
            continue
        if rx["path"] and not (path and rx["path"].search(path)):
            continue
        if rx["path_not"] and path and rx["path_not"].search(path):
            continue
        if rx["command"]:
            if not code or not rx["command"].search(code):           # nowhere in the code: at no position either
                continue
            if positions is None:
                positions = command_positions(code)
            if not any(rx["command"].match(code, p) for p in positions):
                continue
        if rx["command_any"] and not (code and rx["command_any"].search(code)):
            continue
        if rx["text"] and not (text and rx["text"].search(text)):
            continue
        if not any(rx[k] for k in ("path", "command", "command_any", "text")):
            continue                                                 # a row with no detector matches nothing
        hits.append(row)
    return hits


def plan_tool(payload, table, seen, budget=TOOL_BUDGET):
    """(text, record, new keys) for one PreToolUse payload. Reads only the skill files of the matched rows."""
    tool, ti = payload.get("tool_name"), payload.get("tool_input")
    rec = {"event": "PreToolUse", "tool": tool, "matched": [], "injected": [], "skipped": [], "bytes": 0}
    if tool not in TOOLS or not isinstance(ti, dict):
        return "", rec, []
    rows = match_rows(table, tool, ti, payload.get("cwd"), rec["skipped"])
    rec["matched"] = [r["id"] for r in rows]
    parsed, blocks = {}, []
    for row in rows:
        skill = row["skill"]
        try:
            if skill not in parsed:
                parsed[skill] = parse_skill(read_skill(skill))
            lines, sections = parsed[skill]
            idx = resolve(row, lines, sections)
        except LookupError:
            rec["skipped"].append({"row": row["id"], "key": f"{skill} § {row['heading']}", "why": "unresolved"})
            continue
        except (OSError, ValueError) as exc:                        # F16: its skill file is missing or unreadable
            rec["skipped"].append({"row": row["id"], "key": f"{skill} § {row['heading']}", "why": "error",
                                   "error": error_name(exc)})
            continue
        label = f"[system1 · {row['id']}] skill {skill}, the governing lines verbatim:"
        blocks.append((row["id"], skill, row["heading"], entry_units(idx, lines), label))
    text, injected, skipped, new = compose(blocks, seen, budget)
    rec["injected"], rec["bytes"] = injected, len(text.encode()) if text else 0
    rec["skipped"] += skipped
    return text, rec, new


# ---------------------------------------------------------------- the prompt path (L3)

def words(text):
    """Lower-case words of three or more characters, in order, a plural `s` folded ("briefs" meets "brief"). A skill's
    name is matched on this sequence as a phrase, stopwords kept."""
    out = []
    for w in TOKEN_RX.findall(text.lower()):
        if len(w) > 4 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
            w = w[:-1]
        out.append(w)
    return out


def tokens(text):
    """The words of `text` as a set, stopwords out."""
    return {w for w in words(text) if w not in STOPWORDS}


def description(text):
    """A skill's frontmatter `description` on one line (a YAML plain, quoted or block scalar, whitespace folded), or ''
    when it has none. Stdlib only; a test holds it equal to PyYAML's reading of every SKILL.md in the tree."""
    m = FRONT_RX.match(text)
    if not m:
        return ""
    lines = m.group(1).split("\n")
    for i, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        first, more = line[len("description:"):].strip(), []
        for nxt in lines[i + 1:]:
            if nxt.strip() and not nxt[0].isspace():
                break                                                    # the next key
            more.append(nxt.strip())
        if first[:1] in ("|", ">"):
            parts = more
        elif first[:1] == "'":                                            # up to the closing quote; '' is a quote
            parts = [re.match(r"(?:[^']|'')*", " ".join([first[1:]] + more)).group(0).replace("''", "'")]
        elif first[:1] == '"':
            parts = [_double_quoted(" ".join([first[1:]] + more))]
        else:
            parts = [re.split(r"\s#", first, 1)[0]] + more                # a plain scalar: " #" starts a comment
        return " ".join(" ".join(parts).split())
    return ""


def _double_quoted(raw):
    """A double-quoted YAML scalar's text up to its closing quote, its escapes resolved."""
    out, k = [], 0
    while k < len(raw) and raw[k] != '"':
        if raw[k] == "\\" and k + 1 < len(raw):
            nx = raw[k + 1]
            if nx == "u" and re.match(r"[0-9a-fA-F]{4}", raw[k + 2:k + 6]):
                out.append(chr(int(raw[k + 2:k + 6], 16)))
                k += 6
                continue
            out.append(DQ_ESCAPES.get(nx, nx))
            k += 2
            continue
        out.append(raw[k])
        k += 1
    return "".join(out)


def one_line(desc, limit=DESCRIPTION_MAX):
    """`desc` cut to `limit` UTF-8 bytes at a word boundary, "…" marking the cut."""
    if len(desc.encode("utf-8")) <= limit:
        return desc
    cut = desc.encode("utf-8")[:limit - len("…".encode("utf-8"))].decode("utf-8", "ignore")
    return (cut.rsplit(" ", 1)[0] if " " in cut else cut).rstrip(" ,;:") + "…"


def skill_files():
    """{skill: [mtime_ns, size]} of every regular SKILL.md one directory below .claude/skills. The corpus follows the
    tree: a skill added or removed changes it with no table edit. A linked skill directory is followed (F17)."""
    import stat
    out = {}
    try:
        names = sorted(os.listdir(SKILLS_DIR))
    except OSError:
        return out
    for name in names:
        try:
            st = os.stat(skill_file(name))
        except OSError:
            continue
        if stat.S_ISREG(st.st_mode):
            out[name] = [st.st_mtime_ns, st.st_size]
    return out


def build_index(files):
    """The prompt path's index of the skills in `files`. skills: [name, description, description tokens, name words,
    first section, end section]; sections: [skill, heading, start, end, token count, heading tokens, non-blank lines
    under the heading]; post: {token: "<how many skills hold it anywhere> <section> <section> ..."}, one string per
    token, split only for the prompt's words (a JSON list of numbers per token loads about four times slower,
    measured). An unreadable skill file is left out (F17)."""
    skills, sections, post = [], [], {}
    for name in sorted(files):
        try:
            text = read_skill(name)
        except (OSError, ValueError):
            continue
        lines, secs = parse_skill(text)
        desc, first = description(text), len(sections)
        held = tokens(desc) | tokens(name.replace("-", " "))
        for h, s, e in secs:
            toks = tokens(h) | tokens("\n".join(lines[s + 1:e]))
            for t in toks:
                post.setdefault(t, [0]).append(len(sections))
            body_lines = sum(1 for x in lines[s + 1:e] if x.strip())
            sections.append([len(skills), h, s, e, len(toks), sorted(tokens(h)), body_lines])
            held |= toks
        for t in held:
            post.setdefault(t, [0])[0] += 1
        skills.append([name, desc, sorted(tokens(desc)), words(name.replace("-", " ")), first, len(sections)])
    avg = sum(x[4] for x in sections) / len(sections) if sections else 1.0
    return {"v": INDEX_VERSION, "files": files, "skills": skills, "sections": sections, "avg": avg,
            "post": {t: " ".join(map(str, v)) for t, v in post.items()}}


def corpus_index(cache_path):
    """The index of every skill in the tree, through <state>/system1-cache.json: rebuilt whole when a SKILL.md is added,
    removed or changed (its mtime or size), else read as it is."""
    files = skill_files()
    try:
        idx = json.loads(read_regular(cache_path).decode("utf-8"))
    except (FileNotFoundError, ValueError):                          # absent or torn: rebuilt below and rewritten
        idx = None
    if not (isinstance(idx, dict) and idx.get("v") == INDEX_VERSION and idx.get("files") == files
            and isinstance(idx.get("skills"), list) and isinstance(idx.get("sections"), list)
            and isinstance(idx.get("post"), dict)):
        idx = build_index(files)
        write_json_atomic(cache_path, idx)
    return idx


def named(name_words, qset, qwords):
    """True when a skill's name words stand in the prompt as a phrase, in order."""
    if not name_words or not qset.issuperset(name_words):
        return False
    n = len(name_words)
    return any(qwords[i:i + n] == name_words for i in range(len(qwords) - n + 1))


def rank_prompt(prompt, idx, project):
    """[(score, skill, heading, start, end, project skill, description)] of the sections that pass, best first, and the
    prompt's word weights {word: section-level idf}. A section's score: its skill's description words (2x their
    skill-level idf), its skill's name when the prompt names it (2x), its heading words (3x their section-level idf) and
    its body (the idf of the prompt words it holds, scaled down for a long section, BM25-style). A lead word is a
    description, heading or name word that at most one skill in e^LEAD_MIN_IDF - 1 holds. A project skill needs two
    lead words and MIN_PROMPT_SCORE, or, for a short prompt, two lead words that carry MIN_COVER of the prompt's
    weight (its words' skill-level idf) and SHORT_MIN_SCORE; with one lead word it needs ONE_LEAD_MIN_SCORE (F5). A
    library skill counts only when the prompt names it, and needs NAMED_MIN_SCORE (so does a named project skill)."""
    import math
    qw = words(prompt[:PROMPT_SCAN_CHARS])
    q = {w for w in qw if w not in STOPWORDS}
    skills, sections, post = idx["skills"], idx["sections"], idx["post"]
    held = {t: post[t].split() for t in q if post.get(t)}              # [skills holding t, then its sections]
    sidf = {t: math.log(1 + len(skills) / int(v[0])) for t, v in held.items() if int(v[0])}
    idf = {t: math.log(1 + len(sections) / (len(v) - 1)) for t, v in held.items() if len(v) > 1}
    mass = sum(sidf.values())                                        # the prompt's weight: what the corpus knows of it
    body = {}
    for t, w in idf.items():
        for j in held[t][1:]:                                        # section ids as strings: no int() per posting
            body[j] = body.get(j, 0.0) + w
    qset, avg, out = set(qw), idx.get("avg") or 1.0, []
    for name, desc, dtoks, nwords, lo, hi in skills:
        own = name in project
        hit = named(nwords, qset, qw) and (len(nwords) > 1 or sidf.get(nwords[0], 0.0) >= LEAD_MIN_IDF)
        if not (own or hit):
            continue                                                 # a library skill counts only when named
        dm = q.intersection(dtoks)
        nset = {w for w in nwords if w not in STOPWORDS} if hit else set()
        base = 2 * sum(sidf.get(t, 0.0) for t in dm) + 2 * sum(sidf.get(t, 0.0) for t in nset)
        dlead = {t for t in dm if sidf.get(t, 0.0) >= LEAD_MIN_IDF} | nset
        for j in range(lo, hi):
            _, h, s, e, n, htoks, body_lines = sections[j]
            if not body_lines:
                continue                                             # a title with nothing under it: nothing to inject
            hm = q.intersection(htoks)
            lead = dlead | {t for t in hm if sidf.get(t, 0.0) >= LEAD_MIN_IDF}
            if not lead:
                continue
            score = base + 3 * sum(idf.get(t, 0.0) for t in hm) + body.get(str(j), 0.0) * (BODY_K1 + 1) / (
                1 + BODY_K1 * (1 - BODY_B + BODY_B * n / avg))
            if hit:
                ok = score >= NAMED_MIN_SCORE
            elif len(lead) > 1:                                      # strong, or a large share of a short prompt
                ok = score >= MIN_PROMPT_SCORE or (
                    score >= SHORT_MIN_SCORE and sum(sidf[t] for t in lead) >= MIN_COVER * mass)
            else:
                ok = score >= ONE_LEAD_MIN_SCORE
            if ok:
                out.append((round(score, 2), name, h, s, e, own, desc))
    out.sort(key=lambda x: (-x[0], x[1], x[3]))
    return out, idf


def plan_prompt(payload, table, seen, cache_path, budget=PROMPT_BUDGET):
    import hashlib
    rec = {"event": "UserPromptSubmit", "matched": [], "injected": [], "skipped": [], "bytes": 0}
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        rec["why"] = "empty"
        return "", rec, []
    if prompt.lstrip().startswith(HARNESS_EVENT_PREFIXES):
        rec["why"] = "harness-event"
        return "", rec, []
    q = tokens(prompt[:PROMPT_SCAN_CHARS])
    if not q:
        rec["why"] = "no-tokens"
        return "", rec, []
    idx = corpus_index(cache_path)
    rec["corpus"] = len(idx["skills"])
    scored, idf = rank_prompt(prompt, idx, set(table.get("project_skills") or ()))
    rec["matched"] = [f"{skill} § {h} ({score})" for score, skill, h, *_ in scored[:5]]
    top = scored[0][0] if scored else 0.0
    chosen = [x for x in scored[:PROMPT_EXCERPTS] if x[0] >= SECOND_EXCERPT_RATIO * top]
    share = budget // PROMPT_EXCERPTS
    texts = []
    for score, skill, h, s, e, own, desc in chosen:
        lines = read_skill(skill).split("\n")
        # The excerpt starts at the entry that shares the most weight with the prompt, else at the section's top.
        best, best_w, start = s + 1, 0.0, None
        for i in range(s + 1, e):
            if not lines[i].strip():
                start = None
                continue
            if start is None or ENTRY_START_RX.match(lines[i]):
                start = i
                j = i
                while j + 1 < e and lines[j + 1].strip() and not ENTRY_START_RX.match(lines[j + 1]):
                    j += 1
                w = sum(idf.get(t, 0.0) for t in q & tokens("\n".join(lines[i:j + 1])))
                if w > best_w:
                    best, best_w = i, w
        label = f"[system1 · prompt] skill {skill}, the section that matches this prompt, verbatim:"
        taken = seen | {k for t in texts for k in t[3]}                   # the first excerpt's lines count as seen
        dkey = None
        if not own and desc:                                             # a library skill: what it is, once a window
            dline = "description: " + one_line(desc)
            if line_key(skill, dline) not in taken:
                label, dkey = label + "\n" + dline, line_key(skill, dline)
        units = [[(i, lines[i])] for i in range(best, e)]
        text, injected, skipped, new = compose([("prompt", skill, h, units, label)], taken, share, pointer_only=True)
        if injected and dkey:
            new.append(dkey)
        for i in injected:                                               # the join keys for the agent's scores (#295)
            i.update(skill=skill, heading=h, score=score, project=own,
                     sha=hashlib.sha256(text.encode("utf-8")).hexdigest()[:16])
        texts.append((text, injected, skipped, new))
    out = [t[0] for t in texts if t[0]]
    new_keys = [k for t in texts for k in t[3]]
    for _, injected, skipped, _ in texts:
        rec["injected"] += injected
        rec["skipped"] += skipped
    text = "\n".join(out)
    rec["bytes"] = len(text.encode()) if text else 0
    return text, rec, new_keys


# ---------------------------------------------------------------- state

def window_id(payload):
    def clean(v, default):
        v = re.sub(r"[^A-Za-z0-9_-]", "_", v)[:80] if isinstance(v, str) else ""
        return v or default
    return f"{clean(payload.get('session_id'), 'nosession')}.{clean(payload.get('agent_id'), 'main')}"


def open_regular(path, flags, follow=False):
    """os.open that never blocks on a FIFO and raises unless the opened object is a regular file (AF-AP-70a). This hook
    runs on every Bash call, so a planted FIFO must not hang it. A state file is never followed through a symlink; a
    skill file or the table may be (`follow`), as a skill directory can be a link (F17)."""
    import stat
    fd = os.open(path, flags | os.O_NONBLOCK | (0 if follow else os.O_NOFOLLOW), 0o600)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise OSError(f"not a regular file: {os.path.basename(path)}")
    return fd


def read_regular(path, follow=False):
    fd = open_regular(path, os.O_RDONLY, follow)
    try:
        chunks = []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(fd)


def write_json_atomic(path, data):
    """Write to <path>.<pid>.tmp, then rename over `path`. A failed write removes its temp file (F9)."""
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d, mode=0o700, exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    fd = open_regular(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    try:
        try:
            view = memoryview(json.dumps(data, sort_keys=True).encode("utf-8"))
            while view:                                              # a short write (a full disk) is never kept
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


def load_seen(path):
    """The window's injected keys. A missing marker is an empty window; any other failure raises (an unreadable
    marker must not turn into re-injecting everything on every call)."""
    try:
        data = json.loads(read_regular(path).decode("utf-8"))
    except FileNotFoundError:
        return set()
    keys = data.get("keys") if isinstance(data, dict) else None
    if not isinstance(keys, list):
        raise ValueError("marker holds no key list")
    return {k for k in keys if isinstance(k, str)}


class WindowLockTimeout(TimeoutError):
    """Another call of this window held its lock past LOCK_WAIT_S."""


class WindowLock:
    """flock on <marker>.lock, held while a call reads the marker, plans and writes the marker back, so two parallel
    tool calls in one window never both inject a line and never drop each other's keys. A lock still held after
    LOCK_WAIT_S (a slow or stuck sibling) raises WindowLockTimeout: the call injects nothing and logs why. A held lock
    costs one silent call, never a repeated or a lost line (F8)."""

    def __init__(self, path):
        self.path, self.fd = path + ".lock", None

    def __enter__(self):
        import fcntl
        d = os.path.dirname(self.path)
        if not os.path.isdir(d):
            os.makedirs(d, mode=0o700, exist_ok=True)
        self.fd = open_regular(self.path, os.O_WRONLY | os.O_CREAT)
        deadline = time.monotonic() + LOCK_WAIT_S
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    os.close(self.fd)
                    raise WindowLockTimeout(f"held over {LOCK_WAIT_S} s") from None
                time.sleep(0.01)

    def __exit__(self, *exc):
        os.close(self.fd)                                            # closing the fd releases the lock
        return False


def log(state, rec):
    try:
        path = os.path.join(state, "system1.jsonl")
        if not os.path.isdir(state):
            os.makedirs(state, mode=0o700, exist_ok=True)
        try:
            if os.path.getsize(path) > LOG_MAX_BYTES:
                os.replace(path, path + ".1")
        except FileNotFoundError:
            pass
        fd = open_regular(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        try:
            os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
        finally:
            os.close(fd)
    except Exception:
        pass                                                         # telemetry never breaks the hook


def reset(payload, state, now):
    """SessionStart: a compaction forgets the compacted window; a resume or a clear forgets every window of the
    session. Markers older than MARKER_MAX_AGE_S are pruned whatever the source."""
    seen_dir = os.path.join(state, "system1-seen")
    src = payload.get("source")
    wid = window_id(payload)
    sid = wid.split(".", 1)[0]
    removed = 0
    names = os.listdir(seen_dir) if os.path.isdir(seen_dir) else []
    for name in names:
        path = os.path.join(seen_dir, name)
        hit = (src == "compact" and name in (wid + ".json", wid + ".json.lock")) or (
            src in ("resume", "clear") and name.startswith(sid + "."))
        try:
            if hit or now - os.stat(path).st_mtime > MARKER_MAX_AGE_S:
                os.unlink(path)
                removed += name.endswith(".json")
        except FileNotFoundError:
            pass
    return {"event": "SessionStart", "source": src if isinstance(src, str) else None, "removed": removed}


# ---------------------------------------------------------------- the hook

def main(argv):
    started = time.monotonic()
    state = os.environ.get("AF_SYSTEM1_STATE") or os.path.join(ROOT, ".jev")
    resetting = argv[1:] == ["--reset"]
    if not resetting and os.path.lexists(os.path.join(state, "system1-off")):     # a dangling link counts (F12)
        return 0
    rec = {"event": None, "tool": None}
    text, wid = "", None
    try:
        payload = json.loads(read_stdin().decode("utf-8") or "null")
        if not isinstance(payload, dict):
            return 0
        rec = {"event": "SessionStart" if resetting else payload.get("hook_event_name"), "tool": payload.get("tool_name")}
        if resetting:
            rec = reset(payload, state, time.time())
        elif rec["event"] in ("PreToolUse", "UserPromptSubmit"):
            wid = window_id(payload)
            marker = os.path.join(state, "system1-seen", wid + ".json")
            table = load_table()
            with WindowLock(marker):
                seen = load_seen(marker)
                if rec["event"] == "PreToolUse":
                    text, rec, new = plan_tool(payload, table, seen)
                else:
                    text, rec, new = plan_prompt(payload, table, seen, os.path.join(state, "system1-cache.json"))
                if new:
                    write_json_atomic(marker, {"keys": sorted(seen | set(new))})
            rec["window"] = wid
        else:
            return 0
    except BaseException as exc:                                     # fail quiet: nothing injected, the type logged
        text = ""
        rec = {"event": rec.get("event"), "tool": rec.get("tool"), "error": error_name(exc)}
        if wid:
            rec["window"] = wid                                      # which window it was (ids only), as in D6
    rec["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["ms"] = round((time.monotonic() - started) * 1000, 1)
    log(state, rec)
    if text:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except BaseException:
        sys.exit(0)
