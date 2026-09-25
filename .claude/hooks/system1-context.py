#!/usr/bin/env python3
"""system1-context.py — the System-1 context layer, parts L1 and L3 (D-090; S1-L1).

Design: docs/research/findings/system1-context/DESIGN-2026-09-25.md, sections L1 and L3. A rule that says "load skill X
before Y" does not load the skill (AF-AP-218: 12 Skill calls in the main transcripts, while the hooks that inject fired
hundreds of times). So this hook injects the governing skill text itself, verbatim, before the agent acts:

  PreToolUse (Write, Edit, Bash)   L1. The tool input (the file path, the written text, the command) is matched against
                                   the situation table, system1-situations.json beside this file. Each matching row's
                                   key lines are injected verbatim from its skill section, then one line
                                   `full details: <skill file> § <heading>`.
  UserPromptSubmit                 L3. The prompt is keyword-matched against the SECTIONS (a skill split at its
                                   headings) of the table's prompt corpus; the best one or two excerpts are injected,
                                   each with its pointer. It runs beside wiki-context.py, never inside it.
  --reset (from session-start.sh)  SessionStart `compact`, `resume` or `clear`: the window's marker is removed.

Once per context window: the key of every injected line goes into a marker, <state>/system1-seen/<session>.<agent>.json
(`agent` is the payload's `agent_id`, present only inside a subagent, which is its own window, else `main`). A line
already in the marker is not injected again; a row whose lines were all injected is skipped as a duplicate.

Budget: at most 2,048 bytes per tool call and 4,096 per prompt, cut at a line boundary; a row that is cut keeps its
pointer. The text is plain: the registration runs this hook through scripts/hook_context.py, which hands it to the
model as additionalContext (plain PreToolUse stdout reaches only the transcript view, AF-AP-172).

Advisory, never a gate: every path exits 0 and nothing blocks. Off switch: the file <state>/system1-off (the reset
still runs, so a marker never outlives its window). Telemetry: one JSON line per decision in <state>/system1.jsonl
(time, event, tool, the situations matched, the keys injected or skipped and why, the bytes); ids, keys and counts only,
never the tool input or the prompt. An exception injects nothing and logs its type.

Latency: no instrument, no network, no model. The prompt path reads the corpus through <state>/system1-cache.json, keyed
on each skill file's mtime and size (it saves about 19 ms per prompt, measured); the tool path parses only the one to
three skill files a call needs, which costs less than loading that cache.

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
MIN_PROMPT_SCORE = 12.0              # below it a prompt injects nothing (noise is worse than absence)
SECOND_EXCERPT_RATIO = 0.75          # a second section only when it scores at least this share of the best one
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
}

HEADING_RX = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOKEN_RX = re.compile(r"[a-z0-9_]{3,}")
# A line that starts a new entry: a heading, a bold lead, a list item, a numbered or lettered item, a table, a quote, a
# fence. Other non-blank lines continue the entry above them.
ENTRY_START_RX = re.compile(r"^\s*(?:\*\*|#{1,6}\s|[-*+]\s|\d+[a-z]?\.\s|\([a-z0-9]{1,3}\)\s|\||>|```)")
# A command position in a shell line: the start, after a separator or a keyword, past variable assignments, an
# interpreter and a directory prefix (so `cd x && FOO=1 bash /abs/scripts/pc.sh` puts `pc.sh` at a command position,
# while `grep 'git commit' f` and `echo "git push"` do not). A row's `command` pattern is matched AT these positions,
# so it names the command word without a directory (the table test holds that). Compiling this prefix once instead of
# into every row's pattern took the table load from 8.1 to 2.5 ms (measured).
CMD_POS = (r"(?:^|[;&|(\n`]|\$\(|\b(?:then|do|else|nohup|setsid|exec|time|sudo|env|xargs|timeout\s+\S+)\s)\s*"
           r"(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*(?:(?:bash|sh|python3?|node|npx|bunx|pnpm\s+dlx|uv\s+run)\s+(?:-\S+\s+)*)?"
           r"(?:\S*/)?")
DETECTORS = ("command", "command_any", "path", "path_not", "text")


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
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


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


# ---------------------------------------------------------------- composing an injection

def compose(blocks, seen, budget):
    """blocks: [(row id, skill, heading, [(line index, line)], label)] in priority order. Fills the budget at line
    boundaries; a row that is cut keeps its pointer; lines in `seen` are left out. Returns (text, injected, skipped,
    new keys); `seen` is not changed."""
    out, used, injected, skipped, new = [], 0, [], [], []
    taken = set(seen)
    for rid, skill, heading, idx_lines, label in blocks:
        key = f"{skill} § {heading}"
        fresh = [(i, ln) for i, ln in idx_lines if ln.strip() and line_key(skill, ln) not in taken]
        if not fresh:
            skipped.append({"row": rid, "key": key, "why": "duplicate"})
            continue
        head, tail = label, skill_pointer(skill, heading)
        room = budget - used - len(head.encode()) - len(tail.encode()) - 2
        body, prev = [], None
        for i, ln in fresh:
            gap = prev is not None and i != prev + 1
            cost = len(ln.encode()) + 1 + (4 if gap else 0)          # "…" plus its newline marks a gap
            if cost > room:
                break
            if gap:
                body.append("…")
            body.append(ln)
            room -= cost
            prev = i
        n = sum(1 for ln in body if ln != "…")
        if not n:
            skipped.append({"row": rid, "key": key, "why": "budget"})
            continue
        block = [head] + body + [tail]
        out.extend(block)
        used += sum(len(x.encode()) + 1 for x in block)
        keys = [line_key(skill, ln) for _, ln in fresh[:n]]
        taken.update(keys)
        new.extend(keys)
        rec = {"row": rid, "key": key, "lines": n, "bytes": sum(len(x.encode()) + 1 for x in block)}
        if n < len(fresh):
            rec["cut"] = len(fresh) - n                              # left for a later call in this window
        injected.append(rec)
    text = "\n".join(out)
    return text, injected, skipped, new


def match_rows(table, tool, ti, cwd):
    path, text, cmd = tool_fields(tool, ti, cwd)
    hits, positions = [], None
    for row in table["rows"]:
        if tool not in row["tools"]:
            continue
        rx = detectors(row)
        if rx["path"] and not (path and rx["path"].search(path)):
            continue
        if rx["path_not"] and path and rx["path_not"].search(path):
            continue
        if rx["command"]:
            if not cmd:
                continue
            if positions is None:
                positions = command_positions(cmd)
            if not any(rx["command"].match(cmd, p) for p in positions):
                continue
        if rx["command_any"] and not (cmd and rx["command_any"].search(cmd)):
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
    rows = match_rows(table, tool, ti, payload.get("cwd"))
    rec["matched"] = [r["id"] for r in rows]
    parsed, blocks = {}, []
    for row in rows:
        skill = row["skill"]
        if skill not in parsed:
            with open(skill_file(skill), encoding="utf-8") as fh:
                parsed[skill] = parse_skill(fh.read())
        lines, sections = parsed[skill]
        try:
            idx = resolve(row, lines, sections)
        except LookupError:
            rec["skipped"].append({"row": row["id"], "key": f"{skill} § {row['heading']}", "why": "unresolved"})
            continue
        label = f"[system1 · {row['id']}] skill {skill}, the governing lines verbatim:"
        blocks.append((row["id"], skill, row["heading"], [(i, lines[i]) for i in idx], label))
    text, injected, skipped, new = compose(blocks, seen, budget)
    rec["injected"], rec["bytes"] = injected, len(text.encode()) if text else 0
    rec["skipped"] += skipped
    return text, rec, new


# ---------------------------------------------------------------- the prompt path (L3)

def tokens(text):
    """Lower-case words of three or more characters, stopwords out, a plural `s` folded ("briefs" meets "brief")."""
    out = set()
    for w in TOKEN_RX.findall(text.lower()):
        if len(w) > 4 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
            w = w[:-1]
        if w not in STOPWORDS:
            out.add(w)
    return out


def corpus_index(corpus, cache_path):
    """{skill: [[heading, start, end, heading tokens, body tokens], ...]} through the mtime-keyed cache."""
    try:
        cache = json.loads(read_regular(cache_path).decode("utf-8"))
    except (FileNotFoundError, ValueError):                          # absent or torn: rebuilt below and rewritten
        cache = None
    if not isinstance(cache, dict) or cache.get("v") != 1 or not isinstance(cache.get("skills"), dict):
        cache = {"v": 1, "skills": {}}
    dirty, out = False, {}
    for skill in corpus:
        st = os.stat(skill_file(skill))
        ent = cache["skills"].get(skill)
        if not ent or ent.get("mtime_ns") != st.st_mtime_ns or ent.get("size") != st.st_size:
            with open(skill_file(skill), encoding="utf-8") as fh:
                lines, sections = parse_skill(fh.read())
            ent = {"mtime_ns": st.st_mtime_ns, "size": st.st_size, "sections": [
                [h, s, e, sorted(tokens(h)), sorted(tokens("\n".join(lines[s + 1:e])))] for h, s, e in sections]}
            cache["skills"][skill] = ent
            dirty = True
        out[skill] = ent["sections"]
    if dirty:
        write_json_atomic(cache_path, cache)
    return out


def plan_prompt(payload, table, seen, cache_path, budget=PROMPT_BUDGET):
    import math
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
    index = corpus_index(table["prompt_corpus"], cache_path)
    secs = [(skill, h, s, e, set(ht), set(bt)) for skill, lst in index.items() for h, s, e, ht, bt in lst]
    df = {t: sum(1 for *_, ht, bt in secs if t in ht or t in bt) for t in q}
    idf = {t: math.log(1 + len(secs) / df[t]) for t in q if df[t]}
    scored = []
    for skill, h, s, e, ht, bt in secs:
        named = tokens(skill.replace("-", " "))
        lead = (q & ht) | (q & named)
        if not lead:
            continue
        score = sum(3 * idf[t] for t in q & ht) + sum(2 * idf[t] for t in q & named) + sum(idf[t] for t in q & bt)
        if score >= MIN_PROMPT_SCORE:
            scored.append((round(score, 2), skill, h, s, e))
    scored.sort(key=lambda x: (-x[0], x[1], x[3]))
    rec["matched"] = [f"{skill} § {h} ({score})" for score, skill, h, s, e in scored[:5]]
    top = scored[0][0] if scored else 0.0
    chosen = [x for x in scored[:PROMPT_EXCERPTS] if x[0] >= SECOND_EXCERPT_RATIO * top]
    share = budget // PROMPT_EXCERPTS
    texts = []
    for score, skill, h, s, e in chosen:
        with open(skill_file(skill), encoding="utf-8") as fh:
            lines = fh.read().split("\n")
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
        texts.append(compose([("prompt", skill, h, [(i, lines[i]) for i in range(best, e)], label)], taken, share))
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


def open_regular(path, flags):
    """os.open for a state file (AF-AP-70a): never blocks on a FIFO, never follows a symlink, and raises unless the
    opened object is a regular file. This hook runs on every Bash call, so a planted FIFO must not hang it."""
    import stat
    fd = os.open(path, flags | os.O_NONBLOCK | os.O_NOFOLLOW, 0o600)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise OSError(f"not a regular file: {os.path.basename(path)}")
    return fd


def read_regular(path):
    fd = open_regular(path, os.O_RDONLY)
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
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d, mode=0o700, exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    fd = open_regular(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    try:
        view = memoryview(json.dumps(data, sort_keys=True).encode("utf-8"))
        while view:                                                  # a short write (a full disk) is never kept
            view = view[os.write(fd, view):]
    finally:
        os.close(fd)
    os.replace(tmp, path)


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


class WindowLock:
    """flock on <marker>.lock, so two parallel tool calls in one window do not both inject the same lines. A lock that
    cannot be taken within LOCK_WAIT_S is skipped (the worst case is one repeated injection)."""

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
                    return self
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
    if not resetting and os.path.exists(os.path.join(state, "system1-off")):
        return 0
    rec = {"event": None, "tool": None}
    text = ""
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
        rec = {"event": rec.get("event"), "tool": rec.get("tool"), "error": type(exc).__name__}
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
