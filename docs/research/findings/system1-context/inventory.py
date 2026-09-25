#!/usr/bin/env python3
"""inventory.py — S1A evidence demand 1: the static inventory (registration layers, scripts, instruments, MCP servers,
skills). Read-only: it reads files and git history and runs version/status commands; it writes nothing but stdout.

Usage: inventory.py {layers|scripts|instruments|mcp|skills|listing} [--usage USAGE_JSON] [--listing-from TRANSCRIPT]
Secret hygiene: settings and MCP config files are parsed as JSON and only hook entries, server NAMES, server types and
command basenames are printed (never env, headers or args). `listing` reads ONE skill_listing attachment of one
transcript and prints skill NAMES with a described/bare flag, nothing else.
"""
import argparse
import collections
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/user/agent-factory")


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=REPO)
        return p.stdout.strip()
    except subprocess.TimeoutExpired:
        return "(timeout)"


def table(header, rows):
    s = "| " + " | ".join(header) + " |\n|" + "|".join("---" for _ in header) + "|\n"
    for r in rows:
        s += "| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |\n"
    return s


def mtime(p):
    try:
        return sh(f"date -u -r {p} +%Y-%m-%dT%H:%MZ")
    except Exception:
        return "absent"


def hook_entries(path):
    d = json.load(open(path))
    out = []
    for ev, entries in (d.get("hooks") or {}).items():
        for e in entries:
            for h in e.get("hooks", []):
                out.append((ev, e.get("matcher") or "(all)", h.get("type"), h.get("timeout"), h.get("command") or ""))
    return out, d


def layers():
    rows = []
    files = [
        ("/root/.claude/launcher-settings.json", "CCR launcher settings (every session in this container)"),
        ("/root/.claude/settings.json", "user settings (every session of user root)"),
        ("/home/user/.claude/settings.json", "project settings of a session rooted in /home/user (the main session)"),
        (str(REPO / ".claude/settings.json"), "project settings of a session rooted in the repo"),
    ]
    for path, scope in files:
        if not os.path.exists(path):
            rows.append([path, scope, "absent", "-", "-", "-"])
            continue
        ents, d = hook_entries(path)
        for ev, m, t, to, cmd in ents:
            short = re.sub(r"\s+", " ", cmd)
            short = short.replace("/home/user/agent-factory", "<repo>").replace("$CLAUDE_PROJECT_DIR", "<repo>")
            rows.append([path, scope, mtime(path), ev, m, short[:220]])
    plugin_rows = []
    inst = json.load(open("/root/.claude/plugins/installed_plugins.json"))["plugins"]
    enabled = json.load(open("/root/.claude/settings.json")).get("enabledPlugins", {})
    for name, recs in inst.items():
        r = recs[0] if isinstance(recs, list) else recs
        root = r.get("installPath")
        hj = Path(root) / "hooks" / "hooks.json"
        evs = []
        if hj.exists():
            d = json.load(open(hj))
            if "modules" in d:
                evs.append("function hook modules: " + ", ".join(d["modules"]))
            for ev, entries in (d.get("hooks") or {}).items():
                for e in entries:
                    for h in e.get("hooks", []):
                        evs.append(f"{ev} [{e.get('matcher') or 'all'}] {os.path.basename((h.get('command') or '').split()[-1]).strip(chr(34))}")
        plugin_rows.append([name, r.get("version"), (r.get("installedAt") or "")[:16], enabled.get(name), "; ".join(evs)])
    print(table(["settings file", "loaded by", "file mtime (UTC)", "event", "matcher", "command (repo path shortened)"], rows))
    print(table(["plugin", "version", "installed at", "enabled", "hook registrations (hooks/hooks.json)"], plugin_rows))


SCRIPTS = [
    "scripts/lane_context.sh", "scripts/jev_context.py", "scripts/jev_locate.py", "scripts/hiccup_scan.py",
    "scripts/chat_tail.py", "scripts/why.sh", "scripts/ap_screen.py", "scripts/report_lint.py", "scripts/hook_context.py",
    "scripts/install_session_hooks.py", "scripts/owner_rulings.py", "scripts/replay_transcript_edits.py",
    "scripts/orient.sh", "scripts/resume-heal.sh", "scripts/lint_delta.py", "scripts/lane_gate.sh",
    "scripts/ripwire_review.sh", "scripts/sentrux_review.sh", "scripts/gn_mcp.py", "scripts/jev.py", "scripts/jev_echo.py",
    "scripts/jev_local.sh", "scripts/laya_systemone_server.py", "scripts/laya_probe.py", "scripts/qwen_jev.py",
    "scripts/no_laya_in_gates.py", ".claude/hooks/edit-snapshot.py", ".claude/hooks/search-intercept.py",
    ".claude/hooks/wiki-context.py", ".claude/hooks/session-start.sh", ".claude/hooks/turn-retro-gate.sh",
    ".claude/hooks/graft-first-nag.py",
]


def purpose(path):
    try:
        lines = (REPO / path).read_text(errors="replace").splitlines()[:40]
    except Exception:
        return "(unreadable)"
    for ln in lines:
        s = ln.strip().strip('"').strip("#").strip()
        if not s or s.startswith("!") or s.startswith("/usr") or s.startswith("-*-") or s in ("'''", '"""'):
            continue
        if ln.lstrip().startswith(("import ", "from ", "set -", "def ", "class ")):
            continue
        return s[:150]
    return "-"


def refs(name):
    """Tracked files naming the script (literal token sweep), grouped."""
    out = sh(f"git grep -l -F {name} -- . ':!docs/research/findings/system1-context'")
    groups = collections.Counter()
    for p in out.splitlines():
        if p.startswith(".claude/hooks/") or p.startswith("scripts/hooks/"):
            groups["hooks"] += 1
        elif p.startswith(".claude/skills/") or p.startswith(".agents/"):
            groups["skills/mirrors"] += 1
        elif p in ("CLAUDE.md", "AGENTS.md", ".hermes.md"):
            groups["instruction files"] += 1
        elif p.startswith(("scripts/", "harness-ports/")):
            groups["scripts"] += 1
        elif p.startswith("tests/"):
            groups["tests"] += 1
        else:
            groups["docs/other"] += 1
    return groups


def scripts(usage):
    inv = collections.Counter()
    for kind in ("main", "subagent", "wf-subagent"):
        for day, c in (usage["bash_invocations"].get(kind) or {}).items():
            for k, v in c.items():
                inv[(kind if kind == "main" else "sub", k)] += v
    rows = []
    for p in SCRIPTS:
        f = REPO / p
        if not f.exists():
            rows.append([p, "absent"] + ["-"] * 7)
            continue
        base = os.path.basename(p)
        first = sh(f"git log --diff-filter=A --format=%cs -- {p} | tail -1") or "untracked"
        last = sh(f"git log -1 --format='%cs %h' -- {p}")
        n = sh(f"git log --format=%h -- {p} | wc -l")
        g = refs(base)
        runs_m = inv[("main", "script:" + base)] + inv[("main", "quoted:script:" + base)]
        runs_s = inv[("sub", "script:" + base)] + inv[("sub", "quoted:script:" + base)]
        rows.append([p, len(f.read_text(errors="replace").splitlines()), first, last, n,
                     ", ".join(f"{k} {v}" for k, v in sorted(g.items())) or "none", runs_m, runs_s, purpose(p)])
    print(table(["path", "lines", "first commit", "last commit", "commits", "tracked files naming it",
                 "Bash runs main", "Bash runs subagent", "first comment or docstring line"], rows))


INSTR = [
    ("graft", "graft --version", "ls graft/INDEX.md && date -u -r graft/INDEX.md +%FT%TZ", "MCP `graft` (user scope)"),
    ("GitNexus", "gitnexus --version", "node .gitnexus/run.cjs status 2>&1 | grep -E 'Indexed:|Indexed commit|Current commit|Status'", "MCP `gitnexus` (user scope)"),
    ("codebase-memory", "/root/.local/bin/codebase-memory-mcp --version",
     "/root/.local/bin/codebase-memory-mcp cli list_projects 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(\"projects:\", [p[\"name\"] for p in d[\"projects\"]])'",
     "MCP `codebase-memory-mcp` (user scope) + `codebase-memory` (.mcp.json)"),
    ("code-review-graph", "/root/venv-crg/bin/code-review-graph --version",
     "/root/venv-crg/bin/code-review-graph status 2>&1 | grep -E 'Nodes|Last updated|Built at commit'", "none"),
    ("ripwire", "ripwire --version", "ls -la --time-style=+%FT%T /root/.local/bin/ripwire | awk '{print $6}'", "none"),
    ("sentrux", "sentrux --version", "ls -d .sentrux && date -u -r .sentrux +%FT%TZ", "none"),
    ("slopo", "command -v slopo || echo 'not on PATH'", "ls /root/.local/bin/slopo /usr/local/bin/slopo 2>&1 | head -2", "none"),
]


def instruments():
    rows = []
    for name, ver, status, mcp in INSTR:
        v = sh(ver).splitlines()
        s = sh(status).replace("\n", "; ")
        rows.append([name, (v[0] if v else "(no output)")[:60], s[:200], mcp])
    prism = sorted(p.name for p in (REPO / ".claude/skills").glob("prism-*") if p.is_dir())
    rows.append(["prism skills", "vendored " + sh("git log --diff-filter=A --format=%cs -- .claude/skills/prism-scan/SKILL.md | tail -1"),
                 f"{len(prism)} dirs: " + ", ".join(prism), "none (skills, loaded by the Skill tool)"])
    print(table(["instrument", "version (command output)", "index / install state (command output)", "MCP registration"], rows))


def mcp():
    rows = []
    pj = json.load(open(REPO / ".mcp.json")).get("mcpServers", {})
    for name, cfg in pj.items():
        rows.append(["project `.mcp.json`", name, cfg.get("type") or ("stdio" if cfg.get("command") else "?"),
                     os.path.basename(cfg.get("command") or "") or "(url)"])
    try:
        uj = json.load(open("/root/.claude.json"))
        for name, cfg in (uj.get("mcpServers") or {}).items():
            rows.append(["user `/root/.claude.json`", name, cfg.get("type") or ("stdio" if cfg.get("command") else "?"),
                         os.path.basename(cfg.get("command") or "") or "(url)"])
        for proj, pc in (uj.get("projects") or {}).items():
            for name, cfg in (pc.get("mcpServers") or {}).items():
                rows.append([f"local, project {proj}", name, cfg.get("type") or ("stdio" if cfg.get("command") else "?"),
                             os.path.basename(cfg.get("command") or "") or "(url)"])
            en = pc.get("enabledMcpjsonServers")
            if en:
                rows.append([f"local, project {proj}", "enabledMcpjsonServers", ", ".join(en), "-"])
    except Exception as exc:
        rows.append(["user `/root/.claude.json`", f"(unreadable: {type(exc).__name__})", "-", "-"])
    ps = json.load(open(REPO / ".claude/settings.json")).get("enabledMcpjsonServers")
    rows.append(["repo `.claude/settings.json`", "enabledMcpjsonServers", ", ".join(ps or []), "-"])
    print(table(["config", "server", "type", "command basename"], rows))


TRIGGER_RX = re.compile(r"\b(use (?:this|it|when|for|before|after|whenever|to\b)|use this skill|load (?:it |this )?(?:when|before|for|whenever|on)|triggers?\b|trigger on|invoke (?:for|when)|when (?:the user|you|asked|working|writing|building|a |an |about|reviewing|designing|creating|dealing)|before (?:any|writing|a |an |editing|committing|dispatching|authoring|starting|using)|whenever|should be used)", re.I)
PROJECT_RX = re.compile(r"(scripts/|\.py\b|\.sh\b|CLAUDE\.md|\bPC\b|bridge|\blane|ledger|Ouroboros|Hermes|OmniRoute|\bLaya\b|\bJev\b|\bgraft\b|GitNexus|AF-AP|\bD-0\d\d|agent-factory|Fable)", re.I)


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    try:
        import yaml
        d = yaml.safe_load(text[3:end])
        return d if isinstance(d, dict) else {}
    except Exception:
        # Not valid YAML (deep-work and anti-hollow-green: an unquoted colon in the description). The harness still
        # lists them, so read the `description:` line the way a lenient parser does and mark the fallback.
        m = re.search(r"^description:[ \t]*(.*)$", text[3:end], re.M)
        return {"description": m.group(1).strip().strip("'\""), "_yaml_invalid": True} if m else {"_yaml_invalid": True}


def skills(listing_json=None):
    classes = {}
    for line in open(REPO / "sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 2 and parts[0].startswith("skills/") and parts[0].endswith("/SKILL.md"):
            classes[parts[0].split("/")[1]] = parts[1]
    listed = json.load(open(listing_json)) if listing_json else {}
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    rows_first_party = []
    for d in sorted(p for p in (REPO / ".claude/skills").iterdir() if p.is_dir()):
        sk = d / "SKILL.md"
        cls = classes.get(d.name, "unclassified")
        text = sk.read_text(errors="replace") if sk.exists() else ""
        fm = frontmatter(text)
        desc = str(fm.get("description") or "").strip()
        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        nfiles = sum(1 for f in d.rglob("*") if f.is_file())
        b = by[cls]
        b["n"].append(1)
        b["skill_bytes"].append(len(text.encode()))
        b["dir_bytes"].append(size)
        b["files"].append(nfiles)
        b["has_desc"].append(1 if desc else 0)
        b["desc_chars"].append(len(desc))
        b["trigger"].append(1 if TRIGGER_RX.search(desc) else 0)
        b["project"].append(1 if PROJECT_RX.search(desc) else 0)
        b["yaml_invalid"].append(1 if fm.get("_yaml_invalid") else 0)
        if listed:
            b["listed_described"].append(1 if listed.get(d.name) == "described" else 0)
            b["listed_bare"].append(1 if listed.get(d.name) == "bare" else 0)
            b["listed_absent"].append(1 if d.name not in listed else 0)
        if cls in ("first-party", "kit-adapted"):
            rows_first_party.append([d.name, cls, len(text.encode()), len(desc), "yes" if TRIGGER_RX.search(desc) else "no",
                                     "yes" if PROJECT_RX.search(desc) else "no", listed.get(d.name, "absent") if listed else "-"])
    rows = []
    tot = collections.defaultdict(list)
    for cls, b in sorted(by.items(), key=lambda kv: -len(kv[1]["n"])):
        for k, v in b.items():
            tot[k].extend(v)
        rows.append(row(cls, b, bool(listed)))
    rows.append(row("**all**", tot, bool(listed)))
    hdr = ["origin class", "dirs", "SKILL.md bytes median", "SKILL.md bytes max", "all files MB", "has description",
           "median description chars", "description has a trigger phrase", "description names a project artifact",
           "frontmatter not valid YAML"]
    if listed:
        hdr += ["listing: described", "listing: name only", "listing: absent"]
    print(table(hdr, rows))
    print(table(["first-party or kit-adapted skill", "class", "SKILL.md bytes", "description chars", "trigger phrase",
                 "project artifact", "in the subagent listing"], rows_first_party))


def row(cls, b, with_listing):
    r = [cls, len(b["n"]), int(statistics.median(b["skill_bytes"])), max(b["skill_bytes"]),
         round(sum(b["dir_bytes"]) / 1e6, 1), sum(b["has_desc"]), int(statistics.median(b["desc_chars"])),
         sum(b["trigger"]), sum(b["project"]), sum(b["yaml_invalid"])]
    if with_listing:
        r += [sum(b["listed_described"]), sum(b["listed_bare"]), sum(b["listed_absent"])]
    return r


def listing(transcript, out):
    """Names in the FIRST full skill_listing attachment of one transcript, each 'described' or 'bare'."""
    res = {}
    with open(transcript, "rb") as fh:
        for line in fh:
            if b"skill_listing" not in line:
                continue
            r = json.loads(line)
            a = r.get("attachment") or {}
            if a.get("type") != "skill_listing" or not a.get("isInitial"):
                continue
            for ln in (a.get("content") or "").splitlines():
                m = re.match(r"^- ([^\s:]+(?::[^\s:]+)*)(: \S)?", ln)
                if m:
                    res[m.group(1)] = "described" if m.group(2) else "bare"
            meta = {"skillCount": a.get("skillCount"), "timestamp": r.get("timestamp"), "chars": len(a.get("content") or "")}
            break
    json.dump(res, open(out, "w"))
    print(json.dumps({"names": len(res), "described": sum(1 for v in res.values() if v == "described"), **meta}))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("what")
    ap.add_argument("--usage")
    ap.add_argument("--listing-from")
    ap.add_argument("--listing-out")
    ap.add_argument("--listing-json")
    a = ap.parse_args()
    if a.what == "layers":
        layers()
    elif a.what == "scripts":
        scripts(json.load(open(a.usage)))
    elif a.what == "instruments":
        instruments()
    elif a.what == "mcp":
        mcp()
    elif a.what == "skills":
        skills(a.listing_json)
    elif a.what == "listing":
        listing(a.listing_from, a.listing_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
