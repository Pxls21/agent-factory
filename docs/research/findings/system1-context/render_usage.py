#!/usr/bin/env python3
"""render_usage.py — turn scan_transcripts.py's usage.json into the markdown tables of the S1A audit, section 2.

Usage: render_usage.py USAGE_JSON > section2.md   (counts only; the input holds no transcript text)
"""
import collections
import json
import sys


def tot(d, sec, kinds):
    c = collections.Counter()
    for k in kinds:
        for day, x in (d[sec].get(k) or {}).items():
            c.update(x)
    return c


def days_of(d, sec, kinds):
    out = collections.defaultdict(collections.Counter)
    for k in kinds:
        for day, x in (d[sec].get(k) or {}).items():
            out[day].update(x)
    return dict(sorted(out.items()))


def table(header, rows):
    s = "| " + " | ".join(header) + " |\n|" + "|".join("---" for _ in header) + "|\n"
    for r in rows:
        s += "| " + " | ".join(str(x) for x in r) + " |\n"
    return s


KINDS = {"main": ["main"], "subagent": ["subagent", "wf-subagent"]}
TOOLS = ["Bash", "Read", "Edit", "Write", "Grep", "Glob", "Agent", "Skill", "ToolSearch", "Monitor", "WebFetch", "WebSearch"]
INSTR = ["graft", "gitnexus", "codebase-memory", "code-review-graph", "ripwire", "sentrux", "slopo"]
WRAP = {"ripwire": "ripwire_review.sh", "sentrux": "sentrux_review.sh"}  # gn_mcp.py is in the gitnexus program set
SCRIPTS = ["lane_context.sh", "jev_context.py", "jev_locate.py", "hiccup_scan.py", "chat_tail.py", "why.sh", "ap_screen.py",
           "report_lint.py", "hook_context.py", "install_session_hooks.py", "owner_rulings.py",
           "replay_transcript_edits.py", "orient.sh", "resume-heal.sh", "lint_delta.py", "lane_gate.sh", "jev.py",
           "jev_echo.py", "jev_local.sh", "laya_probe.py", "laya_systemone_server.py", "qwen_jev.py",
           "no_laya_in_gates.py", "wiki-context.py", "edit-snapshot.py", "search-intercept.py", "graft-first-nag.py",
           "turn-retro-gate.sh", "session-start.sh", "test_summary.sh", "pc_suite.sh", "pc_lane.sh", "safe_commit.sh",
           "push_clean.sh", "anchor_edit.py", "ci_gate.py", "vendored_manifest.py", "ooo_mcp.py", "setup.sh"]
HOOK_CARRIERS = ("attach:", "stop_hook_summary", "tool_result:error", "user:str")
# One CANONICAL carrier per marker, so one injection is counted once: a Stop block is in `hookErrors` AND echoed as the
# "Stop hook feedback" user turn; the aegis and cbm texts sit in `hook_additional_context` AND in the `hook_success`
# stdout. The cbm marker is the generic word "codebase-memory", so only its hook attachments count; the fast-jev-output
# footer is written INTO the Bash tool output, so an ordinary tool_result is its carrier.
CANONICAL = {
    "EDIT SNAPSHOT": ("attach:hook_additional_context",), "READ CONTEXT": ("attach:hook_additional_context",),
    "GRAFT-FIRST nag": ("attach:hook_additional_context",), "aegis session": ("attach:hook_additional_context",),
    "honey session": ("attach:hook_additional_context",), "honey subagent worker": ("attach:hook_additional_context",),
    "honey subagent reviewer": ("attach:hook_additional_context",),
    "cbm augment": ("attach:hook_additional_context", "attach:hook_system_message"),
    "TURN-END RETRO": ("stop_hook_summary",), "git-check stop": ("stop_hook_summary",),
    "SEARCH INTERCEPT": ("tool_result:error",), "QUIRK GUARD": ("tool_result:error",),
    "fast-jev-output footer": ("tool_result:ok",),
}


def injected(marker, carrier):
    return carrier.startswith(CANONICAL.get(marker, ("attach:hook_success",)))
MARKER_ORDER = ["EDIT SNAPSHOT", "READ CONTEXT", "[wiki live-state (prompt)", "[wiki match", "[incident match",
                "wiki live-state (session start)", "setup banner", "orient layer 0", "TURN-END RETRO", "GRAFT-FIRST nag",
                "SEARCH INTERCEPT", "QUIRK GUARD", "cbm augment", "aegis session", "honey session",
                "honey subagent worker", "honey subagent reviewer", "fast-jev-output footer", "git-check stop"]


def main() -> int:
    d = json.load(open(sys.argv[1]))
    out = []
    files = [f for f in d["files"] if not f.get("excluded")]
    excl = [f["file"] for f in d["files"] if f.get("excluded")]
    rows = []
    for kind in ("main", "subagent", "wf-subagent", "wf-journal"):
        fs = [f for f in files if f["kind"] == kind]
        if not fs:
            continue
        firsts = [f["first_ts"] for f in fs if f["first_ts"]]
        lasts = [f["last_ts"] for f in fs if f["last_ts"]]
        rows.append([kind, len(fs), sum(f["records"] for f in fs), round(sum(f["bytes"] for f in fs) / 1e6, 1),
                     min(firsts)[:16] if firsts else "(no timestamps)", max(lasts)[:16] if lasts else "(no timestamps)",
                     sum(f["bad_lines"] for f in fs)])
    out.append("### 2.1 The corpus\n\n" + table(["kind", "files", "records", "MB", "first record (UTC)", "last record (UTC)",
                                                 "unparseable lines"], rows))
    out.append("\nExcluded: " + ", ".join(excl) + " (this lane's own transcript, written while the scan ran).\n")
    import datetime as _dt
    rpd = d.get("records_per_day", {})
    alld = sorted({x for k in rpd.values() for x in k if x != "no-ts"})
    if alld:
        d0, d1 = _dt.date.fromisoformat(alld[0]), _dt.date.fromisoformat(alld[-1])
        gap = [str(d0 + _dt.timedelta(i)) for i in range((d1 - d0).days + 1) if str(d0 + _dt.timedelta(i)) not in alld]
        out.append("\nDays with no record in any file: " + (", ".join(gap) or "none") + ". Days with main records: " +
                   " ".join(x[5:] for x in sorted(rpd.get("main", {})) if x != "no-ts") + ". Days with subagent records: " +
                   " ".join(x[5:] for x in sorted(set(rpd.get("subagent", {})) | set(rpd.get("wf-subagent", {}))) if x != "no-ts") + ".\n")
    at = collections.Counter()
    for f in files:
        if f.get("agentType"):
            at[f["agentType"]] += 1
    out.append("\nSubagent files by agent type (from each `*.meta.json`): " +
               ", ".join(f"{k} {v}" for k, v in at.most_common()) + ".\n")

    for label, kinds in KINDS.items():
        byday = days_of(d, "tool_calls", kinds)
        rows = []
        grand = collections.Counter()
        for day, c in byday.items():
            grand.update(c)
            mcp = sum(v for k, v in c.items() if k.startswith("mcp__"))
            task = sum(v for k, v in c.items() if k.startswith("Task"))
            other = sum(c.values()) - sum(c.get(t, 0) for t in TOOLS) - mcp - task
            rows.append([day, sum(c.values())] + [c.get(t, 0) for t in TOOLS] + [task, mcp, other])
        mcp = sum(v for k, v in grand.items() if k.startswith("mcp__"))
        task = sum(v for k, v in grand.items() if k.startswith("Task"))
        other = sum(grand.values()) - sum(grand.get(t, 0) for t in TOOLS) - mcp - task
        rows.append(["**total**", sum(grand.values())] + [grand.get(t, 0) for t in TOOLS] + [task, mcp, other])
        out.append(f"\n### 2.2{'a' if label == 'main' else 'b'} Tool calls per day, {label} "
                   f"({' + '.join(kinds)})\n\n" + table(["day", "all"] + TOOLS + ["Task*", "mcp__*", "other"], rows))
        rest = [(k, v) for k, v in grand.most_common() if k not in TOOLS and not k.startswith("mcp__") and not k.startswith("Task")]
        out.append("\n'other' holds: " + ", ".join(f"{k} {v}" for k, v in rest) + ".\n")

    out.append("\n### 2.3 MCP tool calls by server\n")
    for label, kinds in KINDS.items():
        byday = days_of(d, "mcp_calls", kinds)
        servers = sorted(tot(d, "mcp_calls", kinds))
        rows = [[day] + [c.get(s, 0) for s in servers] for day, c in byday.items()]
        t = tot(d, "mcp_calls", kinds)
        rows.append(["**total**"] + [t.get(s, 0) for s in servers])
        out.append(f"\n{label}:\n\n" + table(["day"] + servers, rows))
    out.append("\nMCP calls by server and tool (all kinds): " +
               ", ".join(f"{k} {v}" for k, v in sorted(d["mcp_tools"].items(), key=lambda kv: -kv[1])) + ".\n")

    out.append("\n### 2.4 Bash runs of each instrument and script\n")
    out.append("\nPattern (stated once for every row): the Bash `command` is split into simple commands on `;` `&&` `||` `|` "
               "newline `$(` backtick and parentheses, AFTER heredoc bodies and quoted strings are removed; env "
               "assignments, wrappers (`nohup setsid time env exec timeout nice stdbuf xargs`) and an interpreter "
               "(`bash sh python python3 node uv run npx bunx`, `-m`) are skipped; the program's basename must equal "
               "the instrument's binary (`graft`; `gitnexus`, `.gitnexus/run.cjs`, `gn_mcp.py`; `codebase-memory-mcp`; "
               "`code-review-graph`; `ripwire`; `sentrux`; `slopo`) or the script's file name. 'quoted' = the same test "
               "inside a quoted string handed to `pc.sh`, `pc_bridge_exec.py`, `bash -c`, `sh -c` or `eval` (a PC-side "
               "or nested run). 'mentions' = the name anywhere in the command text (a `cat`, a `git log`, a commit "
               "message also count). A run inside a Python heredoc (`subprocess.run([...])`) or inside another script "
               "is NOT counted here (`lane_context.sh` runs the quartet; the edit-snapshot hook runs `gitnexus impact`; "
               "see 2.6).\n")
    for label, kinds in KINDS.items():
        inv = tot(d, "bash_invocations", kinds)
        men = tot(d, "bash_mentions", kinds)
        rows = []
        for i in INSTR:
            w = WRAP.get(i)
            rows.append([i, inv.get("instr:" + i, 0), inv.get("quoted:instr:" + i, 0),
                         (f"{w} {inv.get('script:' + w, 0)}" if w else "-"), men.get("instr:" + i, 0)])
        out.append(f"\n{label}, instruments:\n\n" + table(["instrument", "runs", "quoted runs", "wrapper runs", "mentions"], rows))
        rows = [[s, inv.get("script:" + s, 0), inv.get("quoted:script:" + s, 0), men.get("script:" + s, 0)] for s in SCRIPTS]
        out.append(f"\n{label}, scripts:\n\n" + table(["script", "runs", "quoted runs", "mentions"], rows))
        sub = collections.Counter()
        for k in kinds:
            sub.update(d["bash_subcommands"].get(k) or {})
        out.append(f"\n{label}, instrument subcommands: " + ", ".join(f"{k} {v}" for k, v in sub.most_common()) + ".\n")
        byday = days_of(d, "bash_invocations", kinds)
        rows = []
        for day, c in byday.items():
            rows.append([day] + [c.get("instr:" + i, 0) + c.get("quoted:instr:" + i, 0) +
                                 (c.get("script:" + WRAP[i], 0) if i in WRAP else 0) for i in INSTR] +
                        [c.get("script:lane_context.sh", 0), c.get("script:ap_screen.py", 0), c.get("script:report_lint.py", 0),
                         c.get("script:hiccup_scan.py", 0), c.get("script:jev_locate.py", 0) + c.get("script:jev_context.py", 0),
                         c.get("script:why.sh", 0) + c.get("script:chat_tail.py", 0)])
        out.append(f"\n{label}, per day (instrument = runs + quoted runs + wrapper runs):\n\n" +
                   table(["day"] + INSTR + ["lane_context.sh", "ap_screen.py", "report_lint.py", "hiccup_scan.py",
                                            "jev_locate+jev_context", "why.sh+chat_tail.py"], rows))

    out.append("\n### 2.5 Skill calls\n")
    for label, kinds in KINDS.items():
        byday = days_of(d, "skill_calls", kinds)
        rows = [[day, sum(c.values()), ", ".join(f"{k} {v}" for k, v in c.most_common())] for day, c in byday.items()]
        t = tot(d, "skill_calls", kinds)
        rows.append(["**total**", sum(t.values()), ", ".join(f"{k} {v}" for k, v in t.most_common())])
        out.append(f"\n{label}, Skill tool calls:\n\n" + table(["day", "calls", "by skill"], rows))
        sl = tot(d, "slash_commands", kinds)
        iv = tot(d, "invoked_skills", kinds)
        out.append(f"\n{label}: slash commands in user records: " + (", ".join(f"/{k} {v}" for k, v in sl.most_common()) or "none") +
                   ". `invoked_skills` attachments (the harness re-attaches a loaded skill after a compaction; one row per "
                   "skill per attachment): " + (", ".join(f"{k} {v}" for k, v in iv.most_common()) or "none") + ".\n")

    out.append("\n### 2.6 Hook injections seen in the records, by marker\n")
    out.append("\nCarriers counted: hook attachments (`hook_success`, `hook_additional_context`, `hook_system_message`), the "
               "`stop_hook_summary` system record's `hookErrors`, a `tool_result` with `is_error` (a PreToolUse block), and "
               "a user string record (the Stop hook's feedback turn). The same marker inside an ordinary `tool_result` "
               "(a `cat` of the hook file, a test run) is NOT an injection. Each marker is counted on ONE canonical carrier "
               "(`CANONICAL` in render_usage.py: the Stop hooks on `hookErrors`, the tool hooks' context on "
               "`hook_additional_context`, the prompt and session hooks on `hook_success`, the blocks on the error "
               "`tool_result`, the fast-jev-output footer in ordinary tool output); the other carriers (echoes such as the "
               "'Stop hook feedback' user turn, and plain mentions) are listed in the last column only.\n")
    for label, kinds in KINDS.items():
        byday = days_of(d, "hook_markers", kinds)
        allm = collections.Counter()
        for day, c in byday.items():
            allm.update(c)
        present = [m for m in MARKER_ORDER if any(k.split("|")[0] == m for k in allm)]
        rows = []
        for day, c in byday.items():
            row = [day]
            for m in present:
                row.append(sum(v for k, v in c.items() if k.split("|")[0] == m and injected(m, k.split("|")[1])))
            rows.append(row)
        tr = []
        for m in present:
            inj = sum(v for k, v in allm.items() if k.split("|")[0] == m and injected(m, k.split("|")[1]))
            quoted = sum(v for k, v in allm.items() if k.split("|")[0] == m and not injected(m, k.split("|")[1]))
            tr.append([m, inj, quoted, ", ".join(f"{k.split('|')[1]} {v}" for k, v in allm.items() if k.split("|")[0] == m)])
        out.append(f"\n{label}, injections per day (hook carriers only):\n\n" + table(["day"] + present, rows))
        out.append(f"\n{label}, totals:\n\n" + table(["marker", "injections (canonical carrier)", "other carriers (echo or mention)", "by carrier"], tr))

    out.append("\n### 2.7 Hook runs, latency and injected size, from the records\n")
    rec = collections.Counter()
    for kinds in KINDS.values():
        pass
    for label, kinds in KINDS.items():
        rec = tot(d, "hook_records", kinds)
        rows = [[k.split("|")[0], k.split("|")[1], k.split("|")[2], v] for k, v in sorted(rec.items(), key=lambda kv: -kv[1])]
        out.append(f"\n{label}, hook records by carrier, event and script (attributed by the record's `command`, else by "
                   "marker):\n\n" + table(["carrier", "event", "script or marker", "records"], rows))
    rows = []
    for k, v in sorted(d["hook_latency_ms"].items()):
        rows.append([k.split("|")[0], k.split("|")[1], v["n"], v["median"], v["p90"], v["max"]])
    out.append("\nLatency (`durationMs` on `hook_success` attachments and on `stop_hook_summary.hookInfos`; all kinds):\n\n" +
               table(["script", "event", "n", "median ms", "p90 ms", "max ms"], rows))
    rows = []
    for k, v in sorted(d["hook_size_chars"].items()):
        if k.startswith("tool_result:error|") and k.split("|")[1] not in ("SEARCH INTERCEPT", "QUIRK GUARD"):
            continue  # only the two PreToolUse blocks inject through an error tool_result; the rest are mentions
        rows.append([k.replace("|", " / "), v["n"], v["median"], v["p90"], v["max"], v["sum"]])
    out.append("\nInjected size in characters (the `content` of the attachment, else its `stdout`; `hookErrors` text for a "
               "Stop block; the error `tool_result` for a PreToolUse block; all kinds; a `hook_success` of size 0 whose "
               "text arrived as a separate `hook_additional_context` record is listed with 0):\n\n" +
               table(["carrier / event / source", "n", "median", "p90", "max", "sum"], rows))
    out.append("\nStop hook outcomes (`stop_hook_summary`): " + ", ".join(f"{k} {v}" for k, v in d["stop_hook_outcomes"].items()) + ".\n")

    out.append("\n### 2.8 The skill listing the model is sent\n")
    rows = []
    for kind, v in d["skill_listing"].items():
        rows.append([kind, v["n"], v["skillCount"]["median"], v["skillCount"]["max"], v["described"]["median"],
                     v["described"]["max"], v["bare"]["median"], v["chars"]["median"], v["chars"]["max"]])
    out.append("\nFrom the `skill_listing` attachments: `skillCount`, and in the listing text the lines `- name: description` "
               "(described) and `- name` alone (bare). Pattern: described = `^- [^\\s:]+(:[^\\s:]+)*: \\S`; bare = a line "
               "that is only `- name`.\n\n" + table(["kind", "listings", "median skills", "max skills",
                                                       "median described", "max described", "median bare",
                                                       "median chars", "max chars"], rows))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
