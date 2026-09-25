#!/usr/bin/env python3
"""scan_transcripts.py — S1A evidence demand 2 (usage), plus the per-event timeline demand 3 reads.

Streams every *.jsonl under the transcript root one line at a time. It never copies a transcript and never prints or
writes transcript text: the outputs hold counts, names, dates, timestamps, byte sizes and tool names only. A marker
(a hook's fixed banner text, listed in MARKERS) is searched inside the record in memory and only its COUNT leaves.

Usage: scan_transcripts.py --out DIR [--root /root/.claude/projects] [--exclude BASENAME ...]
Writes DIR/usage.json (aggregates) and DIR/events.jsonl (one line per instrument or script run, MCP call and Skill
call: timestamp, file kind, file id, category, name; nothing else).

File kinds: main = <root>/<project>/<session>.jsonl; subagent = <session>/subagents/agent-*.jsonl;
wf-subagent = <session>/subagents/workflows/*/agent-*.jsonl; wf-journal = the workflows' journal.jsonl.
"""
import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

# ---- hook markers: the fixed banner text each hook prints (read from the hook sources, 2026-09-25) -------------------
MARKERS = {
    "EDIT SNAPSHOT": "EDIT SNAPSHOT ·",                         # .claude/hooks/edit-snapshot.py (Edit/Write)
    "READ CONTEXT": "READ CONTEXT ·",                           # .claude/hooks/edit-snapshot.py (Read)
    "[wiki live-state (prompt)": "[wiki live-state",                 # .claude/hooks/wiki-context.py
    "wiki live-state (session start)": "── wiki live-state:",  # .claude/hooks/session-start.sh
    "[wiki match": "[wiki match:",                                   # wiki-context.py
    "[incident match": "[incident match:",                           # wiki-context.py
    "wiki-context tail": "[wiki-context: excerpts are a MAP",        # wiki-context.py
    "setup banner": "agent-factory setup: done in",                  # session-start.sh
    "orient layer 0": "orient: layer 0",                             # scripts/orient.sh via session-start.sh
    "TURN-END RETRO": "TURN-END RETRO",                              # .claude/hooks/turn-retro-gate.sh
    "GRAFT-FIRST nag": "GRAFT-FIRST (owner mandate",                 # .claude/hooks/graft-first-nag.py
    "SEARCH INTERCEPT": "SEARCH INTERCEPT (search-intercept.py)",    # .claude/hooks/search-intercept.py
    "QUIRK GUARD": "QUIRK GUARD (search-intercept.py",               # search-intercept.py
    "honey session": "Honey mode is ACTIVE",                         # honey plugin honey-session.js
    "honey subagent worker": "Apply Honey: write the minimum code",  # honey-subagent.js
    "honey subagent reviewer": "Report findings tersely: id",        # honey-subagent.js
    "aegis session": "You have Aegis",                               # aegis plugin session-start
    "fast-jev-output footer": "[fast-jev-output ",                   # fast-jev-output function hook
    "git-check stop": "Please commit and push these changes",        # /root/.claude/stop-hook-git-check.sh
    "cbm augment": "codebase-memory",                                # codebase-memory-mcp hook-augment (count it on hook carriers only)
}

# ---- Bash: instruments and scripts ----------------------------------------------------------------------------------
# An INVOCATION is a simple command (the command split on ; && || | newline $( backtick and parentheses) whose program,
# after env assignments, wrappers (nohup setsid time env exec timeout nice stdbuf xargs cd-free) and an interpreter
# (bash sh python python3 node uv/uvx run npx bunx), has one of these basenames. A MENTION is the name anywhere in
# the command text (a cat, a grep, a git log on the file also count there).
INSTRUMENT_PROGRAMS = {
    "graft": {"graft"},
    "gitnexus": {"gitnexus", "run.cjs", "gn_mcp.py"},
    "codebase-memory": {"codebase-memory-mcp"},
    "code-review-graph": {"code-review-graph"},
    "ripwire": {"ripwire", "ripwire_review.sh"},
    "sentrux": {"sentrux", "sentrux_review.sh"},
    "slopo": {"slopo"},
}
SCRIPT_NAMES = [
    "lane_context.sh", "jev_context.py", "jev_locate.py", "hiccup_scan.py", "chat_tail.py", "why.sh", "ap_screen.py",
    "report_lint.py", "hook_context.py", "install_session_hooks.py", "owner_rulings.py", "replay_transcript_edits.py",
    "orient.sh", "resume-heal.sh", "lint_delta.py", "lane_gate.sh", "test_summary.sh", "pc_lane.sh", "pc_suite.sh",
    "safe_commit.sh", "push_clean.sh", "anchor_edit.py", "ooo_mcp.py", "wiki-context.py", "edit-snapshot.py",
    "search-intercept.py", "graft-first-nag.py", "turn-retro-gate.sh", "session-start.sh", "setup.sh", "ci_gate.py",
    "vendored_manifest.py", "jev.py", "jev_echo.py", "jev_local.sh", "laya_systemone_server.py", "laya_probe.py",
    "qwen_jev.py", "no_laya_in_gates.py", "gn_mcp.py", "ripwire_review.sh", "sentrux_review.sh",
]
# Known subcommand words per instrument (anything else is counted as "?").
SUBCOMMANDS = {
    "graft": {"ask", "skeleton", "skeletons", "build", "index", "status", "find", "trace", "callers", "map", "mcp", "check",
              "telemetry", "refresh", "grep", "doctor", "init", "serve", "--version", "--help"},
    "gitnexus": {"impact", "context", "detect-changes", "detect_changes", "analyze", "query", "status", "cypher", "explain",
                 "trace", "list", "serve", "mcp", "wiki", "clean", "rename", "check", "--version", "--help"},
    "codebase-memory": {"cli", "hook-augment", "install", "index", "--version", "--help"},
    "code-review-graph": {"query", "build", "update", "impact", "status", "serve", "--version", "--help"},
    "ripwire": {"map", "for", "callers", "impact", "exercises", "test-gate", "edit-check", "skipped", "--version", "--help"},
    "sentrux": {"save", "compare", "check", "scan", "--version", "--help"},
    "slopo": {"review", "--version", "--help"},
}
HEREDOC_RX = __import__("re").compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", __import__("re").S)
QUOTE_RX = __import__("re").compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")
RUNNER_RX = __import__("re").compile(r"(?:pc\.sh|pc_bridge_exec\.py|\s-c|\beval)\s*$")
MENTION_RX = {
    "graft": re.compile(r"(?<![\w./-])graft\s+(ask|skeleton|build|find|trace|callers|map|status|index|refresh)\b"),
    "gitnexus": re.compile(r"gitnexus|\.gitnexus/run\.cjs|gn_mcp\.py"),
    "codebase-memory": re.compile(r"codebase-memory-mcp"),
    "code-review-graph": re.compile(r"code-review-graph"),
    "ripwire": re.compile(r"ripwire"),
    "sentrux": re.compile(r"sentrux"),
    "slopo": re.compile(r"\bslopo\b"),
}
SPLIT_RX = re.compile(r"\|\||&&|;|\||\n|\$\(|`|\(|\)")
ASSIGN_RX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
WRAPPERS = {"nohup", "setsid", "time", "env", "exec", "sudo", "nice", "ionice", "command", "stdbuf", "xargs", "then",
            "do", "else", "!", "{"}
INTERPRETERS = {"bash", "sh", "python", "python3", "node", "uv", "uvx", "npx", "bunx", "pnpm", "/root/venv-agent-factory/bin/python", "/root/venv-agent-factory/bin/python3"}


def programs(cmd: str):
    """(basename, next-token) of every simple command's program in a Bash command string."""
    out = []
    for simple in SPLIT_RX.split(cmd):
        toks = simple.strip().split()
        i = 0
        while i < len(toks):
            t = toks[i]
            if ASSIGN_RX.match(t) or t in WRAPPERS:
                i += 1
                continue
            if t == "timeout":
                i += 1
                while i < len(toks) and (toks[i].startswith("-") or re.fullmatch(r"[0-9.]+[smhd]?", toks[i])):
                    i += 1
                continue
            base = os.path.basename(t)
            if base in INTERPRETERS or t in INTERPRETERS or re.fullmatch(r"python3?(\.\d+)?", base):
                i += 1
                if base in ("uv", "pnpm") and i < len(toks) and toks[i] in ("run", "dlx", "exec"):
                    i += 1
                while i < len(toks) and toks[i].startswith("-") and toks[i] not in ("-m",):
                    i += 1
                if i < len(toks) and toks[i] == "-m":
                    i += 1
                continue
            break
        if i < len(toks):
            base = os.path.basename(toks[i]).split("@")[0]
            nxt = toks[i + 1] if i + 1 < len(toks) else ""
            out.append((base, nxt))
    return out


def _count(cmd: str, inv, sub, prefix: str):
    for base, nxt in programs(cmd):
        for inst, names in INSTRUMENT_PROGRAMS.items():
            if base in names:
                if base == "run.cjs" and ".gitnexus" not in cmd:
                    continue
                inv[prefix + "instr:" + inst] += 1
                word = nxt if nxt in SUBCOMMANDS.get(inst, ()) else "?"
                if inst == "codebase-memory" and word == "cli":
                    m = re.search(r"\bcli\s+([a-z_]+)", cmd)
                    word = "cli " + (m.group(1) if m else "?")
                sub[prefix + inst + " " + word] += 1
        if base in SCRIPT_NAMES:
            inv[prefix + "script:" + base] += 1


def classify_bash(cmd: str):
    """Invocations at top level (heredoc bodies and quoted strings removed first), invocations inside a quoted string
    handed to a runner (pc.sh, pc_bridge_exec.py, bash -c, sh -c, eval) prefixed "quoted:", and mentions anywhere."""
    inv = collections.Counter()
    sub = collections.Counter()
    body = HEREDOC_RX.sub("<<HEREDOC", cmd)
    quoted = []

    def keep(m):
        start = m.start()
        if RUNNER_RX.search(body[max(0, start - 40):start]):
            quoted.append(m.group(0)[1:-1])
        return "Q"
    top = QUOTE_RX.sub(keep, body)
    _count(top, inv, sub, "")
    for q in quoted:
        _count(q, inv, sub, "quoted:")
    men = collections.Counter()
    for inst, rx in MENTION_RX.items():
        if rx.search(cmd):
            men["instr:" + inst] += 1
    for s in SCRIPT_NAMES:
        if s in cmd:
            men["script:" + s] += 1
    return inv, sub, men


HOOK_SCRIPTS = ["edit-snapshot.py", "search-intercept.py", "session-start.sh", "wiki-context.py", "turn-retro-gate.sh",
                "graft-first-nag.py", "cbm-code-discovery-gate", "cbm-session-reminder", "cbm-subagent-reminder",
                "honey-session.js", "honey-subagent.js", "logcompress-hook.js", "run-hook.cmd",
                "stop-hook-git-check.sh", "stop-hook-reply-gate.py", "user-prompt-submit-reply-reminder.py",
                "session-start-git-identity.sh", "wiki-stop-gate.sh"]


def hook_script(cmd: str) -> str:
    for s in HOOK_SCRIPTS:
        if s in (cmd or ""):
            return s
    if "echo" in (cmd or "") or "printf" in (cmd or ""):
        return "probe:echo-hook"  # the task #214 visibility probes (2026-09-24), inline echo commands
    return "other"


def text_of(v) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return json.dumps(v, ensure_ascii=False)


def markers_in(text: str):
    return [m for m, s in MARKERS.items() if s in text]


def file_kind(p: Path, root: Path):
    rel = p.relative_to(root).parts
    if len(rel) == 2:
        return "main", rel[0]
    if "workflows" in rel:
        return ("wf-journal" if p.name == "journal.jsonl" else "wf-subagent"), rel[0]
    return "subagent", rel[0]


def pct(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    k = min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))
    return s[k]


def summ(xs):
    return {"n": len(xs), "median": pct(xs, 0.5), "p90": pct(xs, 0.9), "max": max(xs) if xs else None,
            "sum": sum(xs) if xs else 0}


def nested():
    return collections.defaultdict(lambda: collections.defaultdict(collections.Counter))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/root/.claude/projects")
    ap.add_argument("--out", required=True)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--only", default="", help="scan only files whose path contains this text (test runs)")
    a = ap.parse_args()
    root = Path(a.root)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(f for f in root.rglob("*.jsonl") if a.only in str(f))

    tool_calls = nested()       # kind -> day -> tool name
    mcp_calls = nested()        # kind -> day -> server
    mcp_tools = collections.Counter()  # "server tool"
    bash_inv = nested()         # kind -> day -> instr:/script:
    bash_men = nested()
    bash_sub = collections.defaultdict(collections.Counter)   # kind -> "graft ask"
    skill_calls = nested()      # kind -> day -> skill
    slash_cmds = nested()       # kind -> day -> /name
    invoked_sk = nested()       # kind -> day -> skill (invoked_skills attachment)
    agent_types = collections.defaultdict(collections.Counter)  # kind -> subagent_type(+model?)
    hook_recs = nested()        # kind -> day -> "carrier|event|script"
    hook_marks = nested()       # kind -> day -> "marker|carrier"
    hook_lat = collections.defaultdict(list)   # "script|event" -> durationMs
    hook_size = collections.defaultdict(list)  # "carrier|event|script-or-marker" -> chars
    stop_blocks = collections.Counter()        # "script|preventedContinuation"
    hook_span = collections.defaultdict(dict)  # kind -> "event:script" -> [first ts, last ts]
    rec_days = collections.defaultdict(collections.Counter)  # kind -> day -> records
    listing = collections.defaultdict(lambda: {"n": 0, "skillCount": [], "names": [], "chars": [], "lines": [],
                                               "described": [], "bare": []})
    file_rows = []
    ev_fh = open(out / "events.jsonl", "w")

    for f in files:
        if f.name in a.exclude:
            file_rows.append({"file": str(f.relative_to(root)), "excluded": True})
            continue
        kind, proj = file_kind(f, root)
        agent_type = None
        if kind in ("subagent", "wf-subagent"):
            m = f.with_suffix(".meta.json")
            if m.exists():
                try:
                    agent_type = json.load(open(m)).get("agentType")
                except Exception:
                    agent_type = None
        fid = f.stem if kind != "main" else proj + "/" + f.stem[:8]
        n = bad = 0
        first = last = None
        with open(f, "rb") as fh:
            for line in fh:
                n += 1
                try:
                    r = json.loads(line)
                except Exception:
                    bad += 1
                    continue
                ts = r.get("timestamp") if isinstance(r, dict) else None
                if not isinstance(ts, str):
                    ts = None
                if ts:
                    first = ts if first is None or ts < first else first
                    last = ts if last is None or ts > last else last
                day = ts[:10] if ts else "no-ts"
                rec_days[kind][day] += 1
                t = r.get("type")
                msg = r.get("message") if isinstance(r.get("message"), dict) else None
                if t == "assistant" and msg and isinstance(msg.get("content"), list):
                    for b in msg["content"]:
                        if not isinstance(b, dict) or b.get("type") != "tool_use":
                            continue
                        name = b.get("name") or "?"
                        tool_calls[kind][day][name] += 1
                        inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                        if name.startswith("mcp__"):
                            parts = name.split("__")
                            server = parts[1] if len(parts) > 2 else "?"
                            mcp_calls[kind][day][server] += 1
                            mcp_tools[server + " " + (parts[2] if len(parts) > 2 else "?")] += 1
                            ev_fh.write(json.dumps({"ts": ts, "kind": kind, "file": fid, "cat": "mcp", "name": server}) + "\n")
                        elif name == "Skill":
                            sk = inp.get("skill") or inp.get("command") or inp.get("name") or "?"
                            sk = str(sk)[:80]
                            skill_calls[kind][day][sk] += 1
                            ev_fh.write(json.dumps({"ts": ts, "kind": kind, "file": fid, "cat": "skill", "name": sk}) + "\n")
                        elif name == "Bash":
                            cmd = inp.get("command") or ""
                            if isinstance(cmd, str) and cmd:
                                inv, sub, men = classify_bash(cmd)
                                for k, v in inv.items():
                                    bash_inv[kind][day][k] += v
                                    ev_fh.write(json.dumps({"ts": ts, "kind": kind, "file": fid, "cat": "bash", "name": k}) + "\n")
                                for k, v in men.items():
                                    bash_men[kind][day][k] += v
                                for k, v in sub.items():
                                    bash_sub[kind][k] += v
                        elif name in ("Agent", "Task"):
                            st = inp.get("subagent_type") or "(none)"
                            agent_types[kind][str(st)[:60] + (" model=" + str(inp.get("model")) if inp.get("model") else " model=(omitted)")] += 1
                elif t == "user" and msg:
                    c = msg.get("content")
                    if isinstance(c, str):
                        for m in re.findall(r"<command-name>/?([^<]{1,80})</command-name>", c):
                            slash_cmds[kind][day][m.strip()] += 1
                        for mk in markers_in(c):
                            hook_marks[kind][day][mk + "|user:str"] += 1
                    elif isinstance(c, list):
                        for b in c:
                            if not isinstance(b, dict):
                                continue
                            if b.get("type") == "tool_result":
                                txt = text_of(b.get("content"))
                                carrier = "tool_result:error" if b.get("is_error") else "tool_result:ok"
                                for mk in markers_in(txt):
                                    hook_marks[kind][day][mk + "|" + carrier] += 1
                                    if carrier == "tool_result:error":
                                        hook_size[carrier + "|" + mk].append(len(txt))
                                        ev_fh.write(json.dumps({"ts": ts, "kind": kind, "file": fid, "cat": "hook", "name": "PreToolUse:" + mk}) + "\n")
                            elif b.get("type") == "text":
                                txt = b.get("text") or ""
                                for m in re.findall(r"<command-name>/?([^<]{1,80})</command-name>", txt):
                                    slash_cmds[kind][day][m.strip()] += 1
                                for mk in markers_in(txt):
                                    hook_marks[kind][day][mk + "|user:text"] += 1
                elif t == "attachment":
                    att = r.get("attachment") if isinstance(r.get("attachment"), dict) else {}
                    at = att.get("type") or "?"
                    if at.startswith("hook"):
                        ev = att.get("hookEvent") or "?"
                        cmd = att.get("command") or ""
                        txt = text_of(att.get("content")) + "\n" + text_of(att.get("stdout")) + "\n" + text_of(att.get("stderr"))
                        mks = markers_in(txt)
                        script = hook_script(cmd) if cmd else ("marker:" + mks[0] if mks else "unattributed")
                        hook_recs[kind][day]["attach:" + at + "|" + ev + "|" + script] += 1
                        hname = ev + ":" + (script if cmd else (mks[0] if mks else script))
                        ev_fh.write(json.dumps({"ts": ts, "kind": kind, "file": fid, "cat": "hook", "name": hname}) + "\n")
                        if ts:
                            fl = hook_span[kind].setdefault(hname, [ts, ts])
                            fl[0] = min(fl[0], ts)
                            fl[1] = max(fl[1], ts)
                        for mk in mks:
                            hook_marks[kind][day][mk + "|attach:" + at] += 1
                        if isinstance(att.get("durationMs"), (int, float)):
                            hook_lat[script + "|" + ev].append(att["durationMs"])
                        size = len(text_of(att.get("content"))) if att.get("content") is not None else len(text_of(att.get("stdout")))
                        hook_size["attach:" + at + "|" + ev + "|" + script].append(size)
                    elif at == "skill_listing":
                        L = listing[kind]
                        L["n"] += 1
                        if isinstance(att.get("skillCount"), int):
                            L["skillCount"].append(att["skillCount"])
                        if isinstance(att.get("names"), list):
                            L["names"].append(len(att["names"]))
                        ct = text_of(att.get("content"))
                        L["chars"].append(len(ct))
                        lines = [x for x in ct.splitlines() if x.startswith("- ")]
                        L["lines"].append(len(lines))
                        L["described"].append(sum(1 for x in lines if re.match(r"^- [^\s:]+(:[^\s:]+)*: \S", x)))
                        L["bare"].append(sum(1 for x in lines if re.fullmatch(r"- [^\s]+", x.strip())))
                    elif at == "invoked_skills":
                        for s in att.get("skills") or []:
                            nm = s.get("name") if isinstance(s, dict) else s
                            invoked_sk[kind][day][str(nm)[:80]] += 1
                elif t == "system" and r.get("subtype") == "stop_hook_summary":
                    infos = r.get("hookInfos") or []
                    errs = text_of(r.get("hookErrors"))
                    for h in infos:
                        if not isinstance(h, dict):
                            continue
                        script = hook_script(h.get("command") or "")
                        hook_recs[kind][day]["stop_hook_summary|Stop|" + script] += 1
                        ev_fh.write(json.dumps({"ts": ts, "kind": kind, "file": fid, "cat": "hook", "name": "Stop:" + script}) + "\n")
                        if ts:
                            fl = hook_span[kind].setdefault("Stop:" + script, [ts, ts])
                            fl[0] = min(fl[0], ts)
                            fl[1] = max(fl[1], ts)
                        if isinstance(h.get("durationMs"), (int, float)):
                            hook_lat[script + "|Stop"].append(h["durationMs"])
                    for mk in markers_in(errs):
                        hook_marks[kind][day][mk + "|stop_hook_summary.hookErrors"] += 1
                        hook_size["stop_hook_summary.hookErrors|" + mk].append(len(errs))
                    stop_blocks["prevented=" + str(r.get("preventedContinuation")) + "|errors=" + str(bool(r.get("hookErrors")))] += 1
        file_rows.append({"file": str(f.relative_to(root)), "kind": kind, "agentType": agent_type, "records": n,
                          "bad_lines": bad, "first_ts": first, "last_ts": last, "bytes": f.stat().st_size})
    ev_fh.close()

    def plain(d):
        if isinstance(d, dict):
            return {k: plain(v) for k, v in d.items()}
        return d

    res = {
        "files": file_rows,
        "tool_calls": plain(tool_calls), "mcp_calls": plain(mcp_calls), "mcp_tools": dict(mcp_tools),
        "bash_invocations": plain(bash_inv), "bash_mentions": plain(bash_men),
        "bash_subcommands": {k: dict(v) for k, v in bash_sub.items()},
        "skill_calls": plain(skill_calls), "slash_commands": plain(slash_cmds), "invoked_skills": plain(invoked_sk),
        "agent_dispatch": {k: dict(v) for k, v in agent_types.items()},
        "hook_records": plain(hook_recs), "hook_markers": plain(hook_marks),
        "hook_latency_ms": {k: summ(v) for k, v in hook_lat.items()},
        "hook_size_chars": {k: summ(v) for k, v in hook_size.items()},
        "stop_hook_outcomes": dict(stop_blocks),
        "hook_first_last": {k: dict(v) for k, v in hook_span.items()},
        "records_per_day": {k: dict(sorted(v.items())) for k, v in rec_days.items()},
        "skill_listing": {k: {"n": v["n"], "skillCount": summ(v["skillCount"]), "names": summ(v["names"]),
                              "chars": summ(v["chars"]), "listed_lines": summ(v["lines"]),
                              "described": summ(v["described"]), "bare": summ(v["bare"])} for k, v in listing.items()},
    }
    (out / "usage.json").write_text(json.dumps(res, indent=1, sort_keys=True))
    print("files scanned:", sum(1 for r in file_rows if not r.get("excluded")), "excluded:",
          sum(1 for r in file_rows if r.get("excluded")), "records:", sum(r.get("records", 0) for r in file_rows),
          "bad lines:", sum(r.get("bad_lines", 0) for r in file_rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
