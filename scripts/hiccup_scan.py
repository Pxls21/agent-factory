#!/usr/bin/env python3
"""Agent progress and hiccups, read from Claude Code transcripts, written as one deterministic page (task #221 step 2).

Streams every input JSONL line by line (never whole); counts records by their real shapes (assistant records with
`usage` and `model`, `tool_use` / `tool_result` blocks with `is_error`, `task_reminder` and `silent_turn_reminder`
attachments, `compact_boundary` records, `"stop_reason": "refusal"`); clusters tool errors by their normalized first
line (for `Exit code N`, plus the next non-empty output line); maps each cluster to an error family from the closed,
committed map `scripts/hiccup_families.tsv` (first matching regex wins; no match = UNCOVERED); writes `docs/HICCUPS.md`.
Ported from the two E4.3 parsers in docs/research/findings/JEV-LEVERAGE-EVIDENCE-2026-09-24.md (jev_e4e5.py and
jev_e5_side.py). No model runs unless --jev is given.

Deterministic (D-8): the same input bytes give the same page bytes. The page clock is the newest transcript timestamp,
never the wall clock, and every table is sorted. Nothing secret reaches the page (D-11): every excerpt is normalized
(URLs -> U, KEY=value -> KEY=V, quoted strings over 40 characters -> S, runs of 20+ [A-Za-z0-9_-] -> T, numbers -> N),
then scrubbed with transcript_export.scrub, then cut at 160 characters; the page stays under 40,000 bytes.

--jev (D-10, advisory, KC-J1b): for each UNCOVERED cluster the page shows (the top-25 table and the new-this-week
rows), a lexical top 8 over the registry row titles (docs/INCIDENT-LOG.md) and the CLAUDE.md `bit 2026-` quirk lines,
then jev.rank over those 8; the best match and its score fill one extra column in both cluster tables. Jev unavailable:
`n/a (<reason>)`. The column never changes any other number on the page.

usage: hiccup_scan.py [--project-dir DIR | --transcript PATH ...] [--limit-bytes N] [--out PATH] [--jev]
                      [--jev-venue auto|local|pc]
exit: 0 page written (one stats line on stdout); 2 bad input (no transcript, a malformed family map, a page over the
size cap: nothing written); 64 usage error. Standard library only.
"""
import argparse
import collections
import datetime
import glob
import hashlib
import math
import os
import re
import statistics
import sys
import time
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from transcript_export import scrub  # noqa: E402  (the repo's structural secret scrubber, tested per class)

DEFAULT_PROJECT_DIR = "/root/.claude/projects/-home-user"
DEFAULT_OUT = os.path.join(ROOT, "docs", "HICCUPS.md")
FAMILIES_TSV = os.path.join(HERE, "hiccup_families.tsv")
REGISTRY_MD = os.path.join(ROOT, "docs", "INCIDENT-LOG.md")
CLAUDE_MD = os.path.join(ROOT, "CLAUDE.md")

PAGE_MAX_BYTES = 40000
CUT = 160
TOP_CLUSTERS = 25
DAYS = 14
WEEK = 7
TOP_TOOLS = 12
NEW_ROWS = 20
AGENT_TOOLS = ("Agent", "Task")
SLEEP_FAMILY = "harness blocked a foreground sleep"
DENIAL_FAMILY = "auto-mode denial"
JEV_TOP = 8
JEV_INSTRUCTIONS = "Does this note explain or fix the error in the query?"   # the wording measured at 12:17Z

# ---------- excerpts (D-11): normalize, then scrub, then cut ----------

_SEPARATORS = {cp: " " for cp in (0x85, 0x2028, 0x2029)}   # built from code points: a typed escape can become the bytes
_CTRL = re.compile(r"[\x00-\x1f\x7f]")
_URL = re.compile(r"[a-z][a-z0-9+.-]*://\S+", re.I)
_KV = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=\S+")
# a quote that opens after a letter or digit is an apostrophe (`don't`), not a string delimiter
_QUOTED = re.compile(r"(?<![A-Za-z0-9])(?:\"[^\"\n]{41,}\"|'[^'\n]{41,}')")
_RUN = re.compile(r"[A-Za-z0-9_-]{20,}")
_NUM = re.compile(r"\d+")


def excerpt(text):
    """Normalize (URLs, KEY=value, long quoted strings, long runs, numbers), THEN scrub, THEN cut at 160 (D-11)."""
    s = str(text).encode("utf-8", "replace").decode("utf-8")      # a lone surrogate from a JSON escape cannot be written
    s = _CTRL.sub(" ", s.translate(_SEPARATORS))
    s = _URL.sub("U", s)
    s = _KV.sub("KEY=V", s)
    s = _QUOTED.sub("S", s)
    s = _RUN.sub("T", s)
    s = _NUM.sub("N", s)
    return scrub(s)[:CUT]


def cluster_key(text):
    """The normalized first line; `Exit code N` adds the next non-empty output line (D-9)."""
    lines = text.splitlines()
    first = lines[0].strip() if lines else ""
    if re.match(r"Exit code \d+", first):
        nxt = next((ln.strip() for ln in lines[1:] if ln.strip()), "")
        first = first + " :: " + nxt
    return excerpt(first)


# ---------- the closed family map (D-9) ----------

def load_families(path=FAMILIES_TSV):
    """[(compiled regex, family, covering rule)] in file order; ValueError on any malformed row."""
    rows, names = [], set()
    with open(path, encoding="utf-8") as fh:
        for no, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 3 or not all(p.strip() for p in parts):
                raise ValueError("%s:%d: want 3 tab-separated fields: regex, family, covering rule" % (path, no))
            try:
                rx = re.compile(parts[0])
            except re.error as e:
                raise ValueError("%s:%d: bad regex: %s" % (path, no, e))
            name = parts[1].strip()
            if name in names:
                raise ValueError("%s:%d: family %r listed twice (one row per family)" % (path, no, name))
            names.add(name)
            rows.append((rx, name, parts[2].strip()))
    for need in (SLEEP_FAMILY, DENIAL_FAMILY):
        if need not in names:
            raise ValueError("%s: family %r is missing (the per-day table counts it)" % (path, need))
    return rows


def family_of(line, families):
    for rx, name, rule in families:
        if rx.search(line):
            return name, rule
    return None, None


# ---------- record parsing ----------

_TS = re.compile(r"^(\d{4}-\d\d-\d\d)T(\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?Z$")


def canon_ts(ts):
    """An ISO-8601 UTC timestamp -> a fixed-width sortable string; None for anything else."""
    if not isinstance(ts, str):
        return None
    m = _TS.match(ts)
    if not m:
        return None
    try:
        datetime.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return "%sT%s.%sZ" % (m.group(1), m.group(2), (m.group(3) or "").ljust(9, "0"))


def _int(v):
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else 0


def result_text(content):
    """(first text part, bytes the model receives: text UTF-8 bytes + image base64 length) -- E4.3's res()."""
    if isinstance(content, str):
        return content, len(content.encode("utf-8", "replace"))
    first, tot = None, 0
    for p in content if isinstance(content, list) else []:
        if isinstance(p, dict) and p.get("type") == "text":
            t = p.get("text") if isinstance(p.get("text"), str) else ""
            tot += len(t.encode("utf-8", "replace"))
            first = t if first is None else first
        elif isinstance(p, dict) and p.get("type") == "image":
            src = p.get("source") if isinstance(p.get("source"), dict) else {}
            tot += len(src.get("data")) if isinstance(src.get("data"), str) else 0
    return first or "", tot


class Scan:
    """Aggregates over every record fed; nothing here reads the wall clock."""

    def __init__(self, families):
        self.families = families
        self.inputs = {"main": [0, 0, 0, 0], "subagent": [0, 0, 0, 0]}   # files, bytes, lines, unparsable
        self.clock = None
        self.day = collections.defaultdict(collections.Counter)
        self.day_models = collections.defaultdict(collections.Counter)
        self.requests = {}              # requestId -> [day of its first record, context tokens of its last record]
        self.refusals = set()           # message ids that stopped with "refusal"
        self.agents = {}                # agent id -> aggregates
        self.agent_calls = {}           # Agent tool_use id -> its description
        self.agent_desc = {}            # agent id -> the excerpt of that description
        self.use = {}                   # tool_use id -> tool name
        self.clusters = {}              # cluster key -> aggregates
        self.tools = {}                 # tool name -> [results, bytes, largest]
        self.task_reminder = [0, 0]     # records, record bytes
        self.counts = collections.Counter()

    def feed(self, path, limit=None):
        kind = "subagent" if os.path.basename(os.path.dirname(path)) == "subagents" else "main"
        m = re.match(r"agent-([A-Za-z0-9]+)\.jsonl$", os.path.basename(path))
        file_agent = m.group(1) if kind == "subagent" and m else None
        acc = self.inputs[kind]
        acc[0] += 1
        nb = 0
        with open(path, "rb") as fh:
            for raw in fh:
                if limit is not None and nb + len(raw) > limit:
                    break
                nb += len(raw)
                acc[1] += len(raw)
                acc[2] += 1
                try:
                    r = json.loads(raw)
                except (ValueError, RecursionError):
                    acc[3] += 1
                    continue
                if not isinstance(r, dict):
                    acc[3] += 1
                    continue
                self.record(r, len(raw), file_agent)

    def _agent(self, aid):
        a = self.agents.get(aid)
        if a is None:
            a = self.agents[aid] = {"models": collections.Counter(), "requests": set(), "errors": 0, "refusals": 0,
                                    "first": None, "last": None}
        return a

    def record(self, r, nbytes, file_agent):
        t = r.get("type")
        ts = canon_ts(r.get("timestamp"))
        day = ts[:10] if ts else None
        if ts and (self.clock is None or ts > self.clock):
            self.clock = ts
        aid = r.get("agentId") if isinstance(r.get("agentId"), str) and r.get("agentId") else file_agent
        if aid is not None:
            a = self._agent(aid)
            if ts:
                a["first"] = ts if a["first"] is None or ts < a["first"] else a["first"]
                a["last"] = ts if a["last"] is None or ts > a["last"] else a["last"]
        m = r.get("message") if isinstance(r.get("message"), dict) else {}
        c = m.get("content")
        if t == "assistant":
            self._assistant(r, m, c, day, aid)
        elif t == "user" and isinstance(c, list):
            self._user(r, c, day, ts, aid)
        elif t == "attachment":
            k = (r.get("attachment") if isinstance(r.get("attachment"), dict) else {}).get("type")
            if k == "task_reminder":
                self.counts["task_reminder"] += 1
                self.task_reminder[0] += 1
                self.task_reminder[1] += nbytes
            elif k == "silent_turn_reminder":
                self.counts["silent_turn_reminder"] += 1
                if day:
                    self.day[day]["silent"] += 1
        elif t == "system" and r.get("subtype") == "compact_boundary":
            self.counts["compaction"] += 1
            if day:
                self.day[day]["compactions"] += 1

    def _assistant(self, r, m, c, day, aid):
        model = m.get("model") if isinstance(m.get("model"), str) else None
        usage = m.get("usage") if isinstance(m.get("usage"), dict) else None
        if model is not None and usage is not None:
            self.counts["assistant_usage_model"] += 1
        if model is not None:
            if day:
                self.day_models[day][model] += 1
            if aid is not None:
                self._agent(aid)["models"][model] += 1
        rid = r.get("requestId") if isinstance(r.get("requestId"), str) and r.get("requestId") else None
        if rid and usage is not None:
            ctx = sum(_int(usage.get(k)) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
            if rid in self.requests:
                self.requests[rid][1] = ctx
            else:
                self.requests[rid] = [day, ctx]
            if aid is not None:
                self._agent(aid)["requests"].add(rid)
        if m.get("stop_reason") == "refusal":
            key = next((v for v in (m.get("id"), rid, r.get("uuid")) if isinstance(v, str) and v), None)
            key = key if key is not None else "record-%d" % sum(self.counts.values())
            if key not in self.refusals:
                self.refusals.add(key)
                self.counts["refusal_stop"] += 1
                if day:
                    self.day[day]["refusals"] += 1
                if aid is not None:
                    self._agent(aid)["refusals"] += 1
        for b in c if isinstance(c, list) else []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                name = b.get("name") if isinstance(b.get("name"), str) and b.get("name") else "?"
                self.counts["tool_use"] += 1
                if day:
                    self.day[day]["tool_calls"] += 1
                uid = b.get("id") if isinstance(b.get("id"), str) else None
                if uid:
                    self.use[uid] = name
                    inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                    desc = inp.get("description")
                    if name in AGENT_TOOLS and isinstance(desc, str) and desc.strip():
                        self.agent_calls[uid] = desc

    def _user(self, r, c, day, ts, aid):
        blocks = [b for b in c if isinstance(b, dict) and b.get("type") == "tool_result"]
        tur = r.get("toolUseResult") if isinstance(r.get("toolUseResult"), dict) else {}
        for b in blocks:
            uid = b.get("tool_use_id") if isinstance(b.get("tool_use_id"), str) else None
            name = self.use.get(uid, "<unmatched>")
            text, size = result_text(b.get("content"))
            self.counts["tool_result"] += 1
            tl = self.tools.setdefault(name, [0, 0, 0])
            tl[0] += 1
            tl[1] += size
            tl[2] = max(tl[2], size)
            if uid in self.agent_calls:
                sub = tur.get("agentId") if len(blocks) == 1 else None
                if not (isinstance(sub, str) and sub):
                    mm = re.search(r"agentId: ?([A-Za-z0-9]+)", text)
                    sub = mm.group(1) if mm else None
                if sub and sub not in self.agent_desc:
                    self.agent_desc[sub] = excerpt(self.agent_calls[uid])
            if b.get("is_error") is not True:
                continue
            self.counts["tool_error"] += 1
            if day:
                self.day[day]["errors"] += 1
            if aid is not None:
                self._agent(aid)["errors"] += 1
            key = cluster_key(text)
            fam, rule = family_of(key, self.families)
            if day and fam == SLEEP_FAMILY:
                self.day[day]["sleep_blocks"] += 1
            if day and fam == DENIAL_FAMILY:
                self.day[day]["denials"] += 1
            cl = self.clusters.get(key)
            if cl is None:
                cl = self.clusters[key] = {"count": 0, "first": None, "last": None, "tools": set(),
                                           "family": fam, "rule": rule}
            cl["count"] += 1
            cl["tools"].add(name)
            if ts:
                cl["first"] = ts if cl["first"] is None or ts < cl["first"] else cl["first"]
                cl["last"] = ts if cl["last"] is None or ts > cl["last"] else cl["last"]


# ---------- the page (D-12) ----------

def _code(text):
    """A table cell holding an excerpt: a code span (so `<...>` stays text), pipes escaped for the table."""
    if text == "":
        return "(empty)"
    fence = "``" if "`" in text else "`"
    pad = " " if fence == "``" else ""
    return fence + pad + text.replace("|", "\\|") + pad + fence


def _plain(text):
    """A plain table cell: pipes escaped, and `<`/`>` as entities so `<synthetic>` is not read as an HTML tag."""
    return str(text).replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def _hm(ts):
    return "%s %s" % (ts[:10], ts[11:16]) if ts else "-"


def _pct(n, d):
    return "%.1f%%" % (100.0 * n / d) if d else "-"


def top_clusters(sc):
    ranked = sorted(sc.clusters.items(), key=lambda kv: (-kv[1]["count"], kv[1]["first"] or "~", kv[0]))
    return ranked[:TOP_CLUSTERS]


def _window(clock, days):
    if not clock:
        return set()
    cdate = datetime.date.fromisoformat(clock[:10])
    return {(cdate - datetime.timedelta(days=i)).isoformat() for i in range(days)}


def new_clusters(sc):
    """Every cluster first seen in the last 7 days, most frequent first (the page shows the first NEW_ROWS)."""
    win7 = _window(sc.clock, WEEK)
    new = [(k, v) for k, v in sc.clusters.items() if v["first"] and v["first"][:10] in win7]
    return sorted(new, key=lambda kv: (-kv[1]["count"], kv[1]["first"], kv[0]))


def jev_targets(sc):
    """The clusters the page shows (the top table, then the new-this-week rows), once each: the --jev column's rows."""
    seen, out = set(), []
    for key, cl in top_clusters(sc) + new_clusters(sc)[:NEW_ROWS]:
        if key not in seen:
            seen.add(key)
            out.append((key, cl))
    return out


def render(sc, source, jev=None, max_agents=None):
    """The page text. `jev` maps a cluster key to its advisory cell; None leaves the column out entirely.
    `max_agents` keeps only the most recently active agents (build_page sets it when the page would pass the cap)."""
    clock = sc.clock
    win14, win7 = _window(clock, DAYS), _window(clock, WEEK)
    total_bytes = sum(v[1] for v in sc.inputs.values())
    L = ["# Agent hiccups and progress", "",
         "Generated by `scripts/hiccup_scan.py` from Claude Code transcripts; do not edit by hand. Deterministic: the "
         "clock is the newest transcript timestamp, never the wall clock. Excerpts are normalized (numbers N, runs of 20+ "
         "identifier characters T, URLs U, assignments KEY=V, quoted strings over 40 characters S), then scrubbed, then "
         "cut at 160 characters. No model runs unless the error table carries the advisory Jev column.", "",
         "Clock: %s" % ((clock[:19] + "Z") if clock else "none (no timestamped record)"), ""]

    L += ["## Inputs", "", "| kind | files | bytes parsed | lines | unparsable lines |", "|---|---:|---:|---:|---:|"]
    for kind in ("main", "subagent"):
        f, b, n, u = sc.inputs[kind]
        L.append("| %s | %d | %d | %d | %d |" % (kind, f, b, n, u))
    tot = [sum(v[i] for v in sc.inputs.values()) for i in range(4)]
    L += ["| total | %d | %d | %d | %d |" % tuple(tot), "", "Source: %s" % source, ""]

    ctx_by_day = collections.defaultdict(list)
    for day, ctx in sc.requests.values():
        if day:
            ctx_by_day[day].append(ctx)
    days = sorted(d for d in set(sc.day) | set(sc.day_models) | set(ctx_by_day) if d in win14)
    L += ["## Per day (last %d days)" % DAYS, "",
          "Context tokens = input + cache-creation + cache-read tokens of each distinct API request (`requestId`); "
          "error rate = errors / tool calls; refusal stops = distinct messages with `stop_reason` `refusal`.", "",
          "| day | tool calls | errors | error rate | compactions | ctx median | ctx p90 | refusal stops | "
          "not-heard reminders | sleep blocks | auto-mode denials |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for d in days:
        c = sc.day.get(d, collections.Counter())
        ctx = sorted(ctx_by_day.get(d, []))
        med = "%d" % statistics.median(ctx) if ctx else "-"
        p90 = "%d" % ctx[int(0.9 * len(ctx))] if ctx else "-"
        L.append("| %s | %d | %d | %s | %d | %s | %s | %d | %d | %d | %d |" % (
            d, c["tool_calls"], c["errors"], _pct(c["errors"], c["tool_calls"]), c["compactions"], med, p90,
            c["refusals"], c["silent"], c["sleep_blocks"], c["denials"]))
    L.append("")

    L += ["## Served model per day (assistant records, last %d days)" % DAYS, "", "| day | models |", "|---|---|"]
    for d in sorted(x for x in sc.day_models if x in win14):
        mix = sorted(sc.day_models[d].items(), key=lambda kv: (-kv[1], kv[0]))
        L.append("| %s | %s |" % (d, " · ".join("%s %d" % (_plain(k), v) for k, v in mix)))
    L.append("")

    recent = sorted(((aid, a) for aid, a in sc.agents.items() if a["last"] and a["last"][:10] in win7),
                    key=lambda kv: (kv[1]["last"], kv[0]), reverse=True)
    hidden = max(0, len(recent) - max_agents) if max_agents is not None else 0
    recent = sorted(recent[:len(recent) - hidden], key=lambda kv: (kv[1]["first"], kv[0]))
    L += ["## Agents (last %d days)" % WEEK, "",
          "One row per subagent transcript active in the window; models are counted per assistant record; turns = "
          "distinct API requests.", "",
          "| agent | description | models | turns | errors | refusal stops | first | last |",
          "|---|---|---|---:|---:|---:|---|---|"]
    for aid, a in recent:
        mix = sorted(a["models"].items(), key=lambda kv: (-kv[1], kv[0]))
        desc = sc.agent_desc.get(aid)
        L.append("| %s | %s | %s | %d | %d | %d | %s | %s |" % (
            _plain(aid), _code(desc) if desc is not None else "-", " · ".join("%s %d" % (_plain(k), v) for k, v in mix) or "-",
            len(a["requests"]), a["errors"], a["refusals"], _hm(a["first"]), _hm(a["last"])))
    if hidden:
        L.append("")
        L.append("%d older agents active in the window are not shown (the page cap)." % hidden)
    L.append("")

    top = top_clusters(sc)
    n_err = sum(v["count"] for v in sc.clusters.values())
    head = "| # | normalized first line | family | covering rule | count | first seen | last seen | tools |"
    rule = "|---:|---|---|---|---:|---|---|---|"
    if jev is not None:
        head += " Jev suggests (advisory) |"
        rule += "---|"
    by_family = collections.Counter()
    for cl in sc.clusters.values():
        by_family[cl["family"] or "UNCOVERED"] += cl["count"]
    L += ["## Error clusters (top %d of %d clusters, %d errors)" % (len(top), len(sc.clusters), n_err), "",
          "Family = the first matching row of `scripts/hiccup_families.tsv`; UNCOVERED = no row matches; covering rule "
          "`none` = no registry row or CLAUDE.md line covers the family.", "",
          "Errors by family: %s." % ", ".join("%s %d" % (_plain(k), v) for k, v in
                                              sorted(by_family.items(), key=lambda kv: (-kv[1], kv[0]))), "", head, rule]
    for i, (key, cl) in enumerate(top, 1):
        row = "| %d | %s | %s | %s | %d | %s | %s | %s |" % (
            i, _code(key), _plain(cl["family"] or "UNCOVERED"), _plain(cl["rule"] or "-"), cl["count"],
            _hm(cl["first"]), _hm(cl["last"]), _plain(", ".join(sorted(cl["tools"]))))
        if jev is not None:
            row += " %s |" % _plain(jev.get(key, "-"))
        L.append(row)
    L.append("")

    tb = sum(v[1] for v in sc.tools.values())
    ranked = sorted(sc.tools.items(), key=lambda kv: (-kv[1][1], kv[0]))
    L += ["## Context cost", "", "Tool results by tool (bytes the model receives: text bytes plus image base64 length).", "",
          "| tool | results | bytes | share | avg | largest |", "|---|---:|---:|---:|---:|---:|"]
    for name, (n, b, big) in ranked[:TOP_TOOLS]:
        L.append("| %s | %d | %d | %s | %d | %d |" % (_plain(name), n, b, _pct(b, tb), b // max(n, 1), big))
    rest = ranked[TOP_TOOLS:]
    if rest:
        n, b = sum(v[0] for _, v in rest), sum(v[1] for _, v in rest)
        L.append("| %d other tools | %d | %d | %s | %d | %d |" % (len(rest), n, b, _pct(b, tb), b // max(n, 1),
                                                                   max(v[2] for _, v in rest)))
    L += ["", "`task_reminder` attachments: %d records, %d bytes, %s of all bytes parsed." % (
        sc.task_reminder[0], sc.task_reminder[1], _pct(sc.task_reminder[1], total_bytes)), ""]

    new = new_clusters(sc)
    head = "| normalized first line | family | count | first seen | tools |"
    rule = "|---|---|---:|---|---|"
    if jev is not None:
        head += " Jev suggests (advisory) |"
        rule += "---|"
    L += ["## New this week (clusters first seen in the last %d days)" % WEEK, "", head, rule]
    for key, cl in new[:NEW_ROWS]:
        row = "| %s | %s | %d | %s | %s |" % (_code(key), _plain(cl["family"] or "UNCOVERED"), cl["count"],
                                            _hm(cl["first"]), _plain(", ".join(sorted(cl["tools"]))))
        if jev is not None:
            row += " %s |" % _plain(jev.get(key, "-"))
        L.append(row)
    if len(new) > NEW_ROWS:
        L += ["", "%d more new clusters are not shown (the page cap)." % (len(new) - NEW_ROWS)]
    return "\n".join(L) + "\n"


def build_page(sc, source, jev=None):
    """The page bytes: every agent of the window when the page fits under the cap, else the most recent ones that fit
    (the page says how many it left out). A page still over the cap is returned as is; main() refuses to write it."""
    page = render(sc, source, jev).encode("utf-8")
    n = sum(1 for a in sc.agents.values() if a["last"])
    while len(page) >= PAGE_MAX_BYTES and n > 0:
        n = max(0, n - 5)
        page = render(sc, source, jev, max_agents=n).encode("utf-8")
    return page


# ---------- the advisory Jev column (D-10) ----------

_WORD = re.compile(r"[a-z][a-z0-9_]{2,}")
_STOP = frozenset("the and for not with this that from are was were has have had but its into when then than any all "
                  "can may one two out off per via use used using key".split())


def _words(text):
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP}


def _quirk_snippet(line, pos, width=300):
    """The sentence (or bold run) of a CLAUDE.md line that holds the `bit 2026-` marker at `pos`."""
    start = max(line.rfind(". ", 0, pos), line.rfind("**", 0, pos))
    start = 0 if start < 0 else start + 2
    end = line.find(")", pos)
    end = len(line) if end < 0 else end + 1
    return line[start:end].strip().strip("*").strip()[-width:]


def load_candidates(registry=REGISTRY_MD, claude=CLAUDE_MD):
    """[(id, text)]: every registry row title, then every CLAUDE.md `bit 2026-` quirk snippet."""
    cands = []
    with open(registry, encoding="utf-8") as fh:
        for ln in fh:
            m = re.match(r"^\| *(AF-AP-\d+) *\|([^|]*)\|", ln)
            if m:
                cands.append((m.group(1), m.group(2).split(" — ")[0].strip()[:300]))
    with open(claude, encoding="utf-8") as fh:
        for no, ln in enumerate(fh, 1):
            for k, mm in enumerate(re.finditer(r"bit 2026-", ln)):
                cands.append(("CLAUDE.md:%d%s" % (no, "#%d" % (k + 1) if k else ""), _quirk_snippet(ln, mm.start())))
    return cands


def lexical_top(query, cands, n=JEV_TOP):
    """The n candidates sharing the most words with the query (cosine over word sets); ties keep file order."""
    q = _words(query)
    scored = []
    for i, (cid, text) in enumerate(cands):
        w = _words(text)
        ov = len(q & w)
        if ov:
            scored.append((-ov / math.sqrt(len(q) * len(w)), i, cid, text))
    scored.sort()
    return [(cid, text) for _, _, cid, text in scored[:n]]


def jev_column(top, venue="auto", rank=None, reason_of=None, cands=None):
    """{cluster key: cell} for the UNCOVERED clusters of `top`; advisory only (KC-J1b). Stops asking after a failure.
    `rank` / `reason_of` default to jev.rank / jev.last_reason (tests inject their own)."""
    if rank is None:
        try:
            import jev as _jev                # scripts/ is on sys.path; only --jev loads it
            rank = _jev.rank
            reason_of = lambda: _jev.last_reason   # noqa: E731
        except Exception as e:                # Jev unavailable, not a crash (D-10)
            why = "jev.py did not import: %s" % type(e).__name__     # `e` is unbound once the block ends
            rank = lambda *a, **k: None   # noqa: E731
            reason_of = lambda: why   # noqa: E731
    reason_of = reason_of or (lambda: None)
    cands = load_candidates() if cands is None else cands
    out, down = {}, None
    for key, cl in top:
        if cl["family"] is not None:
            continue
        pool = lexical_top(key, cands)
        if not pool:
            out[key] = "n/a (no lexical candidate)"
            continue
        if down is not None:
            out[key] = "n/a (%s)" % down
            continue
        res = rank(key, [{"id": cid, "text": text} for cid, text in pool], instructions=JEV_INSTRUCTIONS, venue=venue,
                   timeout=60)
        if not isinstance(res, dict) or not res.get("ranking"):
            down = excerpt(reason_of() or "no answer")
            out[key] = "n/a (%s)" % down
            continue
        best_id, best = res["ranking"][0]
        out[key] = "%s %.4f" % (best_id, best)
    return out


# ---------- the command ----------

class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write("hiccup_scan: %s\n" % message)
        sys.exit(64)


def main(argv=None):
    ap = _Parser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--project-dir", help="scan DIR/*.jsonl and DIR/*/subagents/*.jsonl (default %s)" % DEFAULT_PROJECT_DIR)
    src.add_argument("--transcript", action="append", help="scan this JSONL (repeatable)")
    ap.add_argument("--limit-bytes", type=int, help="stop reading each file before this many bytes")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--jev", action="store_true", help="fill the advisory Jev column for UNCOVERED clusters")
    ap.add_argument("--jev-venue", choices=("auto", "local", "pc"), default="auto")
    a = ap.parse_args(argv)
    if a.limit_bytes is not None and a.limit_bytes < 1:
        ap.error("--limit-bytes must be a positive integer")
    try:
        families = load_families()
    except (OSError, ValueError) as e:
        sys.stderr.write("hiccup_scan: family map: %s\n" % e)
        return 2
    if a.transcript:
        paths = list(a.transcript)
        missing = [p for p in paths if not os.path.isfile(p)]
        if missing:
            sys.stderr.write("hiccup_scan: no such transcript: %s\n" % missing[0])
            return 2
        source = "%d transcript(s) given with --transcript" % len(paths)
    else:
        d = a.project_dir or DEFAULT_PROJECT_DIR
        paths = sorted(glob.glob(os.path.join(d, "*.jsonl"))) + sorted(glob.glob(os.path.join(d, "*", "subagents", "*.jsonl")))
        if not paths:
            sys.stderr.write("hiccup_scan: no transcript under %s\n" % d)
            return 2
        # the directory's path stays off the page: the same input bytes under another path give the same page (D-8)
        source = "the project directory's `*.jsonl` and `*/subagents/*.jsonl`"
    source += "; byte limit per file: %s" % (a.limit_bytes if a.limit_bytes else "none")
    sc = Scan(families)
    for p in paths:
        sc.feed(p, a.limit_bytes)
    col, jev_note = None, ""
    if a.jev:
        t0 = time.monotonic()
        col = jev_column(jev_targets(sc), venue=a.jev_venue)
        filled = sum(1 for v in col.values() if not v.startswith("n/a"))
        jev_note = " jev: uncovered_shown=%d filled=%d run_s=%.1f" % (len(col), filled, time.monotonic() - t0)
    page = build_page(sc, source, jev=col)
    if len(page) >= PAGE_MAX_BYTES:
        sys.stderr.write("hiccup_scan: the page is %d bytes, over the %d-byte cap; nothing written\n" % (len(page), PAGE_MAX_BYTES))
        return 2
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as fh:
        fh.write(page)
    tot = [sum(v[i] for v in sc.inputs.values()) for i in range(4)]
    uncovered = sum(1 for v in sc.clusters.values() if v["family"] is None)
    print("hiccup_scan: files=%d bytes=%d lines=%d unparsable=%d assistant_usage_model=%d tool_use=%d tool_result=%d "
          "errors=%d clusters=%d uncovered=%d task_reminder=%d silent_turn_reminder=%d compactions=%d refusal_stops=%d "
          "clock=%s page=%s page_bytes=%d sha256=%s%s" % (
              tot[0], tot[1], tot[2], tot[3], sc.counts["assistant_usage_model"], sc.counts["tool_use"],
              sc.counts["tool_result"], sc.counts["tool_error"], len(sc.clusters), uncovered, sc.counts["task_reminder"],
              sc.counts["silent_turn_reminder"], sc.counts["compaction"], sc.counts["refusal_stop"],
              (sc.clock[:19] + "Z") if sc.clock else "none", a.out, len(page), hashlib.sha256(page).hexdigest(), jev_note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
