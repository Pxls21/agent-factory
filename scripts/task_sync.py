#!/usr/bin/env python3
"""task_sync.py - the harness task list as a synced view of the ledger (task #339, D-102; brief LS-B7).

The ledger (`todo/BUILD-TASKLIST.md`) is the one store. This script reads the dated lines of its LIVE section
(`## 2.`), derives each ledger task's newest status event, and writes the harness's task files for the tasks that are
pending or in progress: one `<id>.json` per task, the harness's keys, `JSON.stringify(task, null, 2)` bytes. A Stop hook
and a SessionStart hook run it, so nobody mirrors the task list by hand (D-102).

THE LINES. A dated line is `**<HEADLINE> - YYYY-MM-DD HH:MxZ<tail>**<body>` (an em dash before the date) inside
`## 2.`. Lines are ordered by their date and ten-minute stamp; only two lines in the same ten-minute bucket fall back to
their order in the file, which is the append order (the section heading says "newest first", but lines are appended at
the end). The section's older date-first blocks (`**2026-09-17 11:56Z - ...**`) and dated lines outside `## 2.` are
counted, not read. A line whose stamp has no time places nothing (its mentions are `unknown`).

THE GRAMMAR (closed; the brief's list). Over each headline, split into clauses at top-level `;`:
  REGISTERED -> pending; DISPATCHED, RUNS, RUNNING, RESUMED, BRIEFED -> in_progress; HOME, LANDED, BUILT ->
  in_progress; CLOSED, DONE, SUPERSEDED, ACCEPTED -> closed (removed from the view). An optional `RE-` prefix counts
  (RE-DISPATCHED); a word right after NOT, NO or NEVER, a hyphenated compound (`done-gate`) and anything in backticks do
  not. A task id is `#NNN` (a list `#1, #2 and #3`, a range `#312-#315`), unless the word before the list is ISSUE(S),
  RUN or PR, or BY (`SUPERSEDED BY #339` names the successor), or the list is possessive (`#214's hooks`): those are
  mentions, never subjects. An id list takes the first event word after it in its clause, else the nearest event word
  before it that no other list took. A parenthetical with no id-bearing event of its own (`(TASK #321)`) takes the
  event nearest to it in its clause; one that carries its own events (`(task #123 closed; J1-4, task #121,
  unblocked)`) gives an id with no event of its own nothing. The parenthetical after the stamp follows the headline's
  last clause the same way. A registration whose line carries `#NNN (backlog...)` or `#NNN REGISTERED (backlog...)` is
  `backlog` (kept out of the view). Any id mention the grammar cannot place is recorded as `unknown` with its line and
  changes no status. A table `## 1b. Task overrides` with rows `| id | status | note |` (status pending, in_progress,
  backlog or closed) wins over the extractor.

THE FILES. subject `t<id>-<slug>` (a kebab slug of at most 40 characters from the registration text: the words after
the id's first body mention on its registration line), description (at most 400 characters, naming the status's event,
its stamp and the newest line's stamp), activeForm, status (`pending` or `in_progress`), blocks [], blockedBy []. The
same ledger gives the same bytes.

USAGE
  task_sync.py --ledger PATH --tasks-dir DIR [--apply] [--quiet] [--allow-dir] [--lock-wait SECONDS]
    Without --apply: print the plan (creates, updates, deletes of DIR's `<digits>.json`, the .highwatermark raise), the
    view and every unknown mention; write nothing but the log line. With --apply: under `flock DIR/.lock`, back up
    DIR's JSON files to `<repo>/.jev/task-sync/backup-<UTC>.tar` (only when the plan changes something), write each file
    by write-then-rename, delete the files that left the view, raise `.highwatermark` to at least the largest placed
    ledger id. --apply refuses a DIR that is not a direct child of the harness's tasks root ($CLAUDE_CONFIG_DIR/tasks,
    else ~/.claude/tasks: /root/.claude/tasks here) unless --allow-dir.
  task_sync.py --hook stop|session-start
    The hook form: the payload on stdin names the session; DIR is `<tasks root>/<session_id>` (the harness's own list-id
    spelling), the ledger is `<repo>/todo/BUILD-TASKLIST.md`. Stop prints nothing on stdout, never exits 2 and never
    blocks: 0 on success; on an error it logs it and, only when the error differs from the previous error line in the
    log, writes one stderr line and exits 1 (the harness shows a non-blocking error once, not every turn). SessionStart
    runs the same sync, prints the view (at most 12 lines) and, if the newest log line is an error, that line; it always
    exits 0.

THE OFF SWITCH. While `<repo>/.jev/task-sync-off` exists, both hooks exit 0 at once, write no task file, print
nothing, and append one `off` line to the log per session; --apply refuses with exit 3; a dry run still prints the plan.

EXIT CODES (CLI): 0 done; 3 refused, nothing written (an unreadable ledger, a parse failure, an empty view, a DIR
outside the root, the off switch, a busy lock, a failed backup or write: the reason on stderr); 2 a usage error.
Every run appends one line to `<repo>/.jev/task-sync/sync.log` (UTC, counts and the plan's digest, or the error).

The lock: `flock DIR/.lock` serializes task_sync runs. The harness takes a different lock (proper-lockfile: a
`DIR/.lock.lock` directory for a create, a `DIR/<id>.json.lock` directory for an update), so it is not excluded by this
one; every write here is a rename, so the harness never reads a torn file (LS-B7 report).
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
import re
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "todo" / "BUILD-TASKLIST.md"
OFF = ROOT / ".jev" / "task-sync-off"
STATE = ROOT / ".jev" / "task-sync"
LOG = STATE / "sync.log"

EXIT_OK, EXIT_REFUSED = 0, 3
LOCK_WAIT_S = 10.0
LOG_TAIL_BYTES = 256 * 1024
VIEW_LINES = 12
SLUG_MAX, DESC_MAX = 40, 400

EM, EN, RSQUO = chr(0x2014), chr(0x2013), chr(0x2019)
EVENTS = {
    "REGISTERED": "pending",
    "DISPATCHED": "in_progress", "RUNS": "in_progress", "RUNNING": "in_progress", "RESUMED": "in_progress",
    "BRIEFED": "in_progress",
    "HOME": "in_progress", "LANDED": "in_progress", "BUILT": "in_progress",
    "CLOSED": "closed", "DONE": "closed", "SUPERSEDED": "closed", "ACCEPTED": "closed",
}
VIEW_STATUSES = ("in_progress", "pending")
OVERRIDE_STATUSES = ("pending", "in_progress", "backlog", "closed")
QUALIFIERS = {"ISSUE", "ISSUES", "RUN", "PR", "PRS"}
NEGATORS = {"NOT", "NO", "NEVER"}
KEYS = ("id", "subject", "description", "activeForm", "status", "blocks", "blockedBy")

EVENT_RE = re.compile(r"(?<![\w\-/.])(?:RE-)?(" + "|".join(EVENTS) + r")(?![\w\-/])", re.IGNORECASE)
ONE_ID = r"#(\d+)(?:\s*[-" + EN + r"]\s*#?(\d+))?"
JOIN = r"(?:\s*,\s*(?:and\s+|AND\s+)?|\s+(?:and|AND|&)\s+|\s*\+\s*|\s*/\s*)"
IDLIST_RE = re.compile(ONE_ID + r"(?:" + JOIN + ONE_ID + r")*")
ONE_ID_RE = re.compile(ONE_ID)
STAMP_RE = re.compile(" " + EM + r" (\d{4})-(\d\d)-(\d\d)(?![\d-])")
TIME_RE = re.compile(r" (\d\d):(\d)([\dx])(?::(\d\d))?Z(?!\w)")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


class Refused(Exception):
    """A run that writes nothing and exits 3; the message is the reason (stable text: the Stop hook compares it)."""


# ---- the ledger ----

def _blank(text: str, pattern: str) -> str:
    return re.sub(pattern, lambda m: " " * len(m.group()), text)


def _paren_groups(text: str) -> list:
    """Top-level paren groups as (start, end, inner); an unclosed group runs to the end of the text."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
            if depth == 0:
                out.append((start, i + 1, text[start + 1:i]))
    if depth > 0:
        out.append((start, len(text), text[start + 1:]))
    return out


def _blank_parens(text: str) -> str:
    chars = list(text)
    for s, e, _ in _paren_groups(text):
        chars[s:e] = " " * (e - s)
    return "".join(chars)


def _split_top(text: str, sep: str = ";") -> list:
    parts, depth, last = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        elif ch == sep and depth == 0:
            parts.append(text[last:i])
            last = i + 1
    parts.append(text[last:])
    return parts


def _words_before(text: str, pos: int, n: int) -> list:
    return [w.upper() for w in WORD_RE.findall(text[:pos])[-n:]]


def _ids(listed: str) -> list:
    out = []
    for m in ONE_ID_RE.finditer(listed):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        out.extend(range(a, b + 1) if 0 <= b - a <= 20 else (a, b))
    return out


def _scan(top: str) -> list:
    """The ordered items of a paren-blanked text: ('ids', pos, [ids]) task id lists, ('ref', pos, [ids]) mentions
    that are not subjects (a qualifier or BY before the list, or a possessive after it), ('ev', pos, WORD) events."""
    items = []
    for m in IDLIST_RE.finditer(top):
        before = _words_before(top, m.start(), 1)
        before = before[0] if before else ""
        if before in QUALIFIERS:
            continue
        possessive = re.match("['" + RSQUO + "][sS]\\b", top[m.end():m.end() + 3]) is not None
        kind = "ref" if before == "BY" or possessive else "ids"
        items.append((kind, m.start(), _ids(m.group())))
    for m in EVENT_RE.finditer(top):
        if not NEGATORS & set(_words_before(top, m.start(), 2)):
            items.append(("ev", m.start(), m.group(1).upper()))
    items.sort(key=lambda t: t[1])
    return items


def _bind_items(items: list, inherited) -> list:
    """(id, WORD or None) for the id lists of one text: the first event after the list, else the nearest earlier event
    no other list took, else the inherited event."""
    out, claimed, later = [], set(), []
    for k, item in enumerate(items):
        if item[0] == "ref":
            out += [(i, None) for i in item[2]]
        if item[0] != "ids":
            continue
        nxt = None
        for j in range(k + 1, len(items)):
            if items[j][0] == "ids":
                break
            if items[j][0] == "ev":
                nxt = j
                break
        if nxt is None:
            later.append(k)
        else:
            claimed.add(nxt)
            out += [(i, items[nxt][2]) for i in item[2]]
    for k in later:
        prev = next((j for j in range(k - 1, -1, -1) if items[j][0] == "ev" and j not in claimed), None)
        word = items[prev][2] if prev is not None else inherited
        out += [(i, word) for i in items[k][2]]
    return out


def _group_is_status(inner: str) -> bool:
    """A parenthetical carries its own status when one of its clauses holds both a task id and an event."""
    for sub in _split_top(inner):
        kinds = {t[0] for t in _scan(_blank_parens(sub))}
        if "ids" in kinds and "ev" in kinds:
            return True
    return False


def _nearest_event(items: list, start: int, end: int):
    before = [t[2] for t in items if t[0] == "ev" and t[1] < start]
    if before:
        return before[-1]
    after = [t[2] for t in items if t[0] == "ev" and t[1] >= end]
    return after[0] if after else None


def _bind(text: str, inherited) -> list:
    items = _scan(_blank_parens(text))
    out = _bind_items(items, inherited)
    for s, e, inner in _paren_groups(text):
        take = None if _group_is_status(inner) else _nearest_event(items, s, e)
        for sub in _split_top(inner):
            out += _bind(sub, take)
    return out


def _stamp(bold: str, lineno: int):
    """(date, (hour, tens of minutes) or None, stamp text, start, end) of a dated headline's stamp: the last
    ` - YYYY-MM-DD` outside every paren; None for a line that carries no stamp. A malformed date or time is a parse
    failure."""
    blank = _blank(bold, r"`[^`]*`")
    found = None
    for m in STAMP_RE.finditer(blank):
        depth = 0
        for ch in blank[:m.start()]:
            depth = depth + 1 if ch == "(" else max(0, depth - 1) if ch == ")" else depth
        if depth == 0:
            found = m
    if found is None:
        return None
    y, mo, d = (int(x) for x in found.groups())
    try:
        date = datetime.date(y, mo, d)
    except ValueError:
        raise Refused(f"parse failure: line {lineno}: bad date {found.group(0).strip()[2:]!r}") from None
    rest = blank[found.end():]
    t = TIME_RE.match(rest)
    if t is None:
        if re.match(r" \d", rest):
            raise Refused(f"parse failure: line {lineno}: malformed time after {found.group(0).strip()[2:]}")
        return date, None, bold[found.start() + 3:found.end()], found.start(), found.end()
    hh, m10, sec = int(t.group(1)), int(t.group(2)), t.group(4)
    if hh > 23 or m10 > 5 or (sec is not None and int(sec) > 59):
        raise Refused(f"parse failure: line {lineno}: malformed time {t.group(0).strip()!r}")
    return date, (hh, m10), bold[found.start() + 3:found.end() + t.end()], found.start(), found.end() + t.end()


def _line_mentions(bold: str, start: int, end: int) -> list:
    """(id, WORD or None) for every task-id mention of one headline."""
    head = _blank(bold[:start], r"`[^`]*`")
    tail = _blank(bold[end:], r"`[^`]*`").lstrip()
    clauses = _split_top(head)
    out = []
    for clause in clauses:
        out += _bind(clause, None)
    if tail.startswith("("):
        s, e, inner = _paren_groups(tail)[0]
        last = _scan(_blank_parens(clauses[-1]))
        take = None if _group_is_status(inner) else _nearest_event(last, len(clauses[-1]), len(clauses[-1]))
        for sub in _split_top(inner):
            out += _bind(sub, take)
        tail = tail[e:].lstrip()
    if tail.startswith(";"):
        for clause in _split_top(tail[1:]):
            out += _bind(clause, None)
    return out


def _clean(text: str) -> str:
    return " ".join(text.replace("`", "").replace("**", "").split())


def _registration_text(tid: int, body: str) -> str:
    """The words after the id's first body mention: an optional name, a parenthetical unless it is a status
    (`(backlog...)`, `(open)`), and the text after a colon, each up to the sentence end."""
    m = re.search(r"(?<![\w#])#" + str(tid) + r"(?!\d)", body)
    if m is None:
        return ""
    rest = re.sub(r"^\s+REGISTERED\b", "", body[m.end():]).lstrip()
    parts, i, depth = [], 0, 0
    while i < len(rest) and rest[i] not in "(:;" and not (rest[i] == "." and rest[i + 1:i + 2] in (" ", "")):
        i += 1
    parts.append(rest[:i])
    rest = rest[i:]
    if rest.startswith("("):
        s, e, inner = _paren_groups(rest)[0]
        if not re.match(r"\s*(backlog\b|open\s*$)", inner, re.IGNORECASE):
            parts.append(inner)
        rest = rest[e:].lstrip()
    if rest.startswith(":"):
        rest, i = rest[1:], 0
        while i < len(rest) and i < 600:
            ch = rest[i]
            depth = depth + 1 if ch == "(" else max(0, depth - 1) if ch == ")" else depth
            if depth == 0 and (ch == ";" or (ch == "." and rest[i + 1:i + 2] in (" ", ""))):
                break
            i += 1
        parts.append(rest[:i])
    return _clean(" ".join(parts))


def _head_text(tid: int, head: str) -> str:
    """The headline clause that names the id, without its ids and TASK words (the title when no body names it)."""
    clause = next((c for c in _split_top(head) if re.search(r"#" + str(tid) + r"(?!\d)", c)), head)
    return _clean(re.sub(r"#\d+|\bTASKS?\b|[()]", " ", clause, flags=re.IGNORECASE))


def _slug(text: str) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())
    if words and words[0] in ("the", "a", "an"):
        words = words[1:]
    slug = ""
    for w in words:
        cand = f"{slug}-{w}" if slug else w
        if len(cand) > SLUG_MAX:
            break
        slug = cand
    return slug or (words[0][:SLUG_MAX] if words else "task")


def _overrides(lines: list) -> dict:
    heads = [i for i, line in enumerate(lines) if re.match(r"## 1b\.", line)]
    if len(heads) > 1:
        raise Refused(f"parse failure: {len(heads)} '## 1b.' override sections (lines {', '.join(str(h + 1) for h in heads)})")
    out = {}
    if not heads:
        return out
    for i in range(heads[0] + 1, len(lines)):
        line = lines[i]
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if [c.lower() for c in cells] == ["id", "status", "note"] or all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        if len(cells) != 3 or not re.fullmatch(r"#?\d+", cells[0]) or cells[1] not in OVERRIDE_STATUSES:
            raise Refused(f"parse failure: line {i + 1}: an override row must be | id | status | note | with a status in "
                          f"{', '.join(OVERRIDE_STATUSES)}")
        tid = int(cells[0].lstrip("#"))
        if tid in out:
            raise Refused(f"parse failure: line {i + 1}: a second override row for #{tid}")
        out[tid] = {"status": cells[1], "note": cells[2], "line": i + 1}
    return out


def extract(text: str) -> dict:
    """The ledger's tasks: {id: {"events": [...], "mentions": [...], "reg": line}} plus the unknown mentions, the
    overrides and the line counts. Raises Refused on a parse failure."""
    lines = text.split("\n")
    start = next((i for i, line in enumerate(lines) if line.startswith("## 2.")), None)
    if start is None:
        raise Refused("parse failure: no '## 2.' LIVE section")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    tasks, unknown = {}, []
    stats = {"dated": 0, "date_only": 0, "legacy": 0, "outside": 0}
    for i, line in enumerate(lines):
        if not line.startswith("**"):
            continue
        close = line.find("**", 2)
        if close < 0:
            continue
        bold, lineno = line[2:close], i + 1
        if not start < i < end:
            stats["outside"] += STAMP_RE.search(bold) is not None
            continue
        if re.match(r"\d{4}-\d\d-\d\d", bold):
            stats["legacy"] += 1
            continue
        found = _stamp(bold, lineno)
        if found is None:
            continue
        date, tkey, stamp, s, e = found
        stats["dated"] += 1
        stats["date_only"] += tkey is None
        key = (date, tkey or (-1, -1), lineno)
        per_line = {}
        for tid, word in _line_mentions(bold, s, e):
            t = tasks.setdefault(tid, {"events": [], "mentions": [], "reg": None})
            t["mentions"].append((key, stamp, lineno, line[close + 2:], bold[:s]))
            if word is None or tkey is None:
                unknown.append((tid, lineno, stamp, _clean(bold[:s])))
                continue
            status = EVENTS[word]
            if word == "REGISTERED":
                if re.search(r"(?<![\w#])#" + str(tid) + r"(?:\s+REGISTERED)?\s*\(backlog\b", line):
                    word, status = "REGISTERED (backlog)", "backlog"
                if t["reg"] is None or key < t["reg"][0]:      # the oldest registration by stamp
                    t["reg"] = (key, stamp, lineno, line[close + 2:], bold[:s])
            per_line[tid] = (word, status)
        for tid, (word, status) in per_line.items():
            tasks[tid]["events"].append((key, stamp, lineno, word, status))
    if stats["dated"] == 0:
        raise Refused("parse failure: the LIVE section holds no dated line")
    return {"tasks": tasks, "unknown": unknown, "overrides": _overrides(lines), "stats": stats,
            "lines": lines}


def build_view(ex: dict) -> dict:
    """{"view": {id: task} for every pending or in-progress task, "status": {id: status} for every placed id}."""
    status, view = {}, {}
    tasks = ex["tasks"]
    for tid in sorted(set(tasks) | set(ex["overrides"])):
        t = tasks.get(tid, {"events": [], "mentions": [], "reg": None})
        events = sorted(t["events"])
        ov = ex["overrides"].get(tid)
        if ov is None and not events:
            continue
        last = events[-1] if events else None
        st = ov["status"] if ov else last[4]
        status[tid] = st
        if st not in VIEW_STATUSES:
            continue
        mentions = sorted(t["mentions"])
        newest = mentions[-1][1] if mentions else "none"
        if t["reg"] is not None:
            _, rstamp, _, body, rhead = t["reg"]
            first = "Registered"
        elif mentions:
            _, rstamp, _, body, rhead = mentions[0]
            first = "First line"
        else:
            rstamp, body, rhead, first = "none", "", "", "Registered"
        text = _registration_text(tid, body) or _head_text(tid, rhead) or _clean((ov or {}).get("note", ""))
        if ov:
            why = f"{st} by the override table ({_clean(ov['note']) or 'no note'})"
        else:
            why = f"{st} from {last[3]} on {last[1]}"
        desc = _clean(f"Ledger task #{tid}: {why}; newest ledger line {newest}. {first} {rstamp}: {text}")
        if len(desc) > DESC_MAX:
            desc = desc[:DESC_MAX - 3].rstrip() + "..."
        view[tid] = {"id": str(tid), "subject": f"t{tid}-{_slug(text)}", "description": desc,
                     "activeForm": f"Working on task #{tid}", "status": st, "blocks": [], "blockedBy": [],
                     "_word": ov and "override" or last[3], "_stamp": (last or (None, newest))[1],
                     "_newest": mentions[-1][0] if mentions else (datetime.date.min, (-1, -1), 0)}
    return {"view": view, "status": status}


def task_bytes(task: dict) -> bytes:
    return json.dumps({k: task[k] for k in KEYS}, indent=2, ensure_ascii=False).encode("utf-8")


# ---- the plan and its application ----

def harness_tasks_root() -> Path:
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(cfg) if cfg else Path.home() / ".claude") / "tasks"


def _hwm(dirpath: Path) -> int:
    try:
        return int((dirpath / ".highwatermark").read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0


def make_plan(view: dict, dirpath: Path, target_hwm: int) -> dict:
    want = {f"{tid}.json": task_bytes(t) for tid, t in view.items()}
    have = {}
    if dirpath.is_dir():
        for p in dirpath.iterdir():
            if re.fullmatch(r"\d+\.json", p.name):
                try:
                    have[p.name] = p.read_bytes()
                except OSError:
                    have[p.name] = None
    ops = []
    for name in sorted(want, key=lambda n: int(n[:-5])):
        if name not in have:
            ops.append(("create", name, want[name]))
        elif have[name] != want[name]:
            ops.append(("update", name, want[name]))
    for name in sorted(set(have) - set(want), key=lambda n: int(n[:-5])):
        ops.append(("delete", name, have[name]))
    old = _hwm(dirpath)
    new = max(old, target_hwm)
    digest = hashlib.sha256()
    for op, name, data in ops:
        digest.update(f"{op} {name} {hashlib.sha256(data or b'').hexdigest() if op != 'delete' else '-'}\n".encode())
    if new != old:
        digest.update(f"highwatermark {new}\n".encode())
    return {"ops": ops, "hwm": (old, new), "digest": digest.hexdigest()[:12]}


def plan_is_empty(plan: dict) -> bool:
    return not plan["ops"] and plan["hwm"][0] == plan["hwm"][1]


def _lock(dirpath: Path, wait_s: float) -> int:
    fd = os.open(dirpath / ".lock", os.O_RDWR | os.O_CREAT, 0o644)
    deadline = time.monotonic() + wait_s
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            if time.monotonic() >= deadline:
                os.close(fd)
                raise Refused(f"lock busy: another process holds {dirpath / '.lock'}; nothing written") from None
            time.sleep(0.05)


def _write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def _backup(dirpath: Path) -> Path:
    STATE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    dest = STATE / f"backup-{stamp}.tar"
    with tarfile.open(dest, "x") as tar:
        for p in sorted(dirpath.glob("*.json")):
            if p.is_file() and not p.is_symlink():
                tar.add(p, arcname=f"{dirpath.name}/{p.name}", recursive=False)
    return dest


def apply_plan(view: dict, dirpath: Path, target_hwm: int, wait_s: float) -> dict:
    """Plan and apply under the lock; the plan is re-read inside it."""
    dirpath.mkdir(parents=True, exist_ok=True)
    fd = _lock(dirpath, wait_s)
    try:
        plan = make_plan(view, dirpath, target_hwm)
        if plan_is_empty(plan):
            return plan
        try:
            plan["backup"] = _backup(dirpath)
        except OSError as exc:
            raise Refused(f"backup failed: {exc.__class__.__name__}: {exc.strerror or exc}; nothing written") from None
        try:
            for op, name, data in plan["ops"]:
                if op == "delete":
                    (dirpath / name).unlink(missing_ok=True)
                else:
                    _write_atomic(dirpath / name, data)
            if plan["hwm"][1] != plan["hwm"][0]:
                _write_atomic(dirpath / ".highwatermark", str(plan["hwm"][1]).encode())
        except OSError as exc:
            raise Refused(f"write failed in {dirpath}: {exc.__class__.__name__}: {exc.strerror or exc}; "
                          f"the backup is {plan['backup'].name}") from None
        return plan
    finally:
        os.close(fd)


# ---- the log ----

def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(kind: str, text: str) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"{_utc()} {kind} {' '.join(text.split())[:600]}\n")


def log_tail() -> list:
    try:
        with open(LOG, "rb") as fh:
            size = fh.seek(0, 2)
            fh.seek(max(0, size - LOG_TAIL_BYTES))
            data = fh.read()
    except OSError:
        return []
    lines = data.decode("utf-8", "replace").splitlines()
    return lines[1:] if size > LOG_TAIL_BYTES else lines


def _kind_rest(line: str):
    parts = line.split(" ", 2)
    return (parts[1], parts[2] if len(parts) > 2 else "") if len(parts) > 1 else ("", "")


def previous_error() -> str:
    for line in reversed(log_tail()):
        kind, rest = _kind_rest(line)
        if kind == "error":
            return rest
    return ""


# ---- one run ----

def off_switch_set() -> bool:
    try:
        os.lstat(OFF)
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return True          # cannot tell: stay inert


def run(ledger: Path, dirpath: Path, apply: bool, allow_dir: bool, wait_s: float) -> dict:
    """One sync: returns the result for printing; raises Refused (nothing written)."""
    if apply and off_switch_set():
        raise Refused(f"off switch set: {OFF} exists; --apply refused (a dry run still prints the plan)")
    if apply and not allow_dir:
        root = harness_tasks_root()
        if Path(os.path.realpath(dirpath)).parent != Path(os.path.realpath(root)):
            raise Refused(f"refused: {dirpath} is not a task dir under {root} (pass --allow-dir for a test dir)")
    try:
        text = ledger.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Refused(f"unreadable ledger {ledger}: {exc.__class__.__name__}: {getattr(exc, 'strerror', None) or exc}") from None
    ex = extract(text)
    built = build_view(ex)
    view = built["view"]
    if not view:
        raise Refused("empty view: the ledger yields no pending or in-progress task; nothing written")
    target = max([tid for tid, st in built["status"].items()] or [0])
    plan = apply_plan(view, dirpath, target, wait_s) if apply else make_plan(view, dirpath, target)
    return {"ex": ex, "built": built, "plan": plan, "dir": dirpath, "ledger": ledger}


def _counts(res: dict) -> str:
    plan, view = res["plan"], res["built"]["view"]
    c = {k: sum(1 for op in plan["ops"] if op[0] == k) for k in ("create", "update", "delete")}
    old, new = plan["hwm"]
    hwm = f"{old}->{new}" if new != old else f"{old}"
    return (f"dir={res['dir']} view={len(view)} create={c['create']} update={c['update']} delete={c['delete']} "
            f"hwm={hwm} digest={plan['digest']}")


def render(res: dict, applied: bool) -> list:
    ex, built, plan = res["ex"], res["built"], res["plan"]
    view, status, st = built["view"], built["status"], ex["stats"]
    by = {s: sum(1 for v in status.values() if v == s) for s in ("in_progress", "pending", "backlog", "closed")}
    placed = set(status)
    unplaced = sorted(set(ex["tasks"]) - placed)
    out = [f"task_sync: {'applied' if applied else 'dry run, nothing written'}",
           f"ledger {res['ledger']}: {st['dated']} dated lines placed ({st['date_only']} with no time); "
           f"{st['legacy']} older date-first lines and {st['outside']} dated lines outside '## 2.' not read",
           f"tasks dir {res['dir']}",
           f"view: {len(view)} tasks ({by['in_progress']} in_progress, {by['pending']} pending); backlog "
           f"{by['backlog']}, closed {by['closed']}, overrides {len(ex['overrides'])}, ids with no status "
           f"{len(unplaced)}, unknown mentions {len(ex['unknown'])}"]
    old, new = plan["hwm"]
    out.append(f"plan: {_counts(res)}" + ("" if applied or not off_switch_set() else f" (off switch {OFF} set)"))
    for op, name, data in plan["ops"]:
        tid = int(name[:-5])
        if op == "delete":
            try:
                was = json.loads(data or b"{}").get("subject", "?")
            except ValueError:
                was = "unreadable"
            out.append(f"  delete {name} (was {was})")
        else:
            out.append(f"  {op} {name} {view[tid]['subject']} [{view[tid]['status']}]")
    if new != old:
        out.append(f"  highwatermark {old} -> {new}")
    out.append("view (the files the plan leaves):")
    for tid in sorted(view):
        v = view[tid]
        out.append(f"  #{tid} {v['status']} {v['subject']} ({v['_word']} {v['_stamp']})")
    out.append("ids with no status (every mention unknown): " + (" ".join(f"#{i}" for i in unplaced) or "none"))
    out.append("unknown mentions (the grammar cannot place them; they change no status):")
    for tid, lineno, stamp, head in ex["unknown"]:
        out.append(f"  #{tid} line {lineno} {stamp}: {head[:140]}")
    return out


def view_lines(res: dict) -> list:
    view = res["built"]["view"]
    tasks = sorted(view.values(), key=lambda v: (v["_newest"], int(v["id"])), reverse=True)
    tasks.sort(key=lambda v: v["status"] != "in_progress")
    n_in = sum(1 for v in tasks if v["status"] == "in_progress")
    out = [f"Task list = the ledger's view (scripts/task_sync.py, D-102): {len(tasks)} open ({n_in} in_progress, "
           f"{len(tasks) - n_in} pending) in {res['dir']}"]
    room = VIEW_LINES - 1 if len(tasks) <= VIEW_LINES - 1 else VIEW_LINES - 2
    for v in tasks[:room]:
        out.append(f"#{v['id']} {v['status']} {v['subject']} ({v['_word']} {v['_stamp']})"[:160])
    if len(tasks) > room:
        out.append(f"+{len(tasks) - room} more: python3 scripts/task_sync.py --ledger todo/BUILD-TASKLIST.md "
                   f"--tasks-dir {res['dir']}"[:160])
    return out


# ---- the hooks ----

def _session_dir(payload: bytes) -> tuple:
    try:
        obj = json.loads(payload.decode("utf-8") or "null")
    except (ValueError, UnicodeDecodeError):
        obj = None
    sid = obj.get("session_id") if isinstance(obj, dict) else None
    if not isinstance(sid, str) or not sid.strip() or len(sid) > 200:
        raise Refused("hook payload: no usable session_id")
    name = re.sub(r"[^A-Za-z0-9_-]", "-", sid)          # the harness's own list-id spelling
    return name, harness_tasks_root() / name


def _log_off_once(payload: bytes, event: str) -> None:
    try:
        name = _session_dir(payload)[0]
    except Refused:
        name = "unknown"
    mark = f"session={name} "
    if not any(_kind_rest(line)[0] == "off" and (_kind_rest(line)[1] + " ").startswith(mark) for line in log_tail()):
        log("off", f"session={name} {event}: {OFF} exists, no task file written")


def hook(event: str) -> int:
    if off_switch_set():        # FIRST: the off switch (LS-B7 item 7)
        try:
            _log_off_once(sys.stdin.buffer.read(1 << 20), event)
        except OSError:
            pass                # the off state is inert by contract: exit 0, nothing shown, even when its log line fails
        return 0
    res, reason = None, ""
    try:
        name, dirpath = _session_dir(sys.stdin.buffer.read(1 << 20))
        res = run(LEDGER, dirpath, apply=True, allow_dir=False, wait_s=LOCK_WAIT_S)
    except Refused as exc:
        reason = str(exc)
    except Exception as exc:     # never a traceback, never exit 2
        reason = f"{event} hook failed: {exc.__class__.__name__}: {exc}"
    shown = False
    try:
        prior = previous_error() if reason else ""
        if reason:
            log("error", reason)
        else:
            log("ok", f"apply {event} {_counts(res)}")
    except Exception as exc:
        reason = reason or f"cannot write {LOG}: {exc.__class__.__name__}: {exc}"
        prior = ""
    if event == "session-start":
        lines = view_lines(res) if res else []
        tail = log_tail()
        if tail and _kind_rest(tail[-1])[0] == "error":
            lines.append(f"task_sync error (newest log line): {tail[-1]}"[:300])
        if lines:
            print("\n".join(lines))
        return 0
    if reason and " ".join(reason.split())[:600] != prior:
        shown = True
        print(f"task_sync: {' '.join(reason.split())[:300]} (logged in .jev/task-sync/sync.log; shown once per new "
              f"error)", file=sys.stderr)
    return 1 if shown else 0


# ---- the command line ----

def _log_quietly(kind: str, text: str) -> None:
    try:
        log(kind, text)
    except OSError as exc:
        print(f"task_sync: cannot append to {LOG}: {exc.__class__.__name__}: {exc}", file=sys.stderr)


def main(argv: list) -> int:
    if argv[:1] == ["--hook"]:              # the hook form never reaches argparse, whose usage error is exit 2
        return hook(argv[1]) if len(argv) == 2 and argv[1] in ("stop", "session-start") else 0
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--tasks-dir", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--allow-dir", action="store_true")
    ap.add_argument("--lock-wait", type=float, default=LOCK_WAIT_S)
    args = ap.parse_args(argv)
    try:
        res = run(args.ledger, args.tasks_dir, args.apply, args.allow_dir, args.lock_wait)
    except Refused as exc:
        print(f"task_sync: {exc}", file=sys.stderr)
        _log_quietly("error", str(exc))
        return EXIT_REFUSED
    _log_quietly("ok", f"{'apply' if args.apply else 'dry'} {_counts(res)}")
    if not args.quiet:
        print("\n".join(render(res, args.apply)))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
