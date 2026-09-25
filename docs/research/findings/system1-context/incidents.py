#!/usr/bin/env python3
"""incidents.py — S1A evidence demand 3: registry rows AF-AP-150..AF-AP-218 against what existed to name their class,
and whether it ran in the two hours before the commit that recorded the row.

Method (row-id cross-reference; blind to a class named in prose without a row id):
  1. Each row is read from the working-tree docs/INCIDENT-LOG.md registry table (| id | mechanism | greppable signature |
     proven instance | status |). Its recording commit = the first commit whose diff ADDS a line `| AF-AP-<n>`
     (`git log --reverse -p -U0 -- docs/INCIDENT-LOG.md`).
  2. "Earlier rows it cites" = the AF-AP ids named in the row text whose own recording commit is older.
  3. At the recording commit's PARENT: the edit-snapshot hook (.claude/hooks/edit-snapshot.py), scripts/ap_screen.py,
     every .claude/skills/*/SKILL.md and CLAUDE.md are searched for each cited id (`git grep` at that revision).
  4. The window is [commit time - 2 h, commit time]. From scan_transcripts.py's events.jsonl: Skill calls, Bash runs of
     ap_screen.py / jev_locate.py / jev_echo.py / the code instruments, and hook injections, per kind (main, subagent).
     A second pass over the transcripts counts, inside each window, the hook carriers (hook attachments, Stop-hook
     errors, error tool_results) that hold `[incident match` and those that hold a cited id. Counts only.

Usage: incidents.py --events EVENTS_JSONL [--root /root/.claude/projects] [--exclude BASENAME] > demand3.md
"""
import argparse
import bisect
import collections
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/user/agent-factory")
LO, HI = 150, 218
ID_RX = re.compile(r"AF-AP-(\d+)\b")
SCREENS = [".claude/hooks/edit-snapshot.py", "scripts/ap_screen.py"]


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def rows():
    out = {}
    for line in (REPO / "docs/INCIDENT-LOG.md").read_text().splitlines():
        m = re.match(r"^\|\s*(?:\*\*)?AF-AP-(\d+)\b", line)
        if m:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            out[int(m.group(1))] = {"cols": cols, "text": line}
    return out


def recording_commits():
    first = {}
    cur = None
    log = git("log", "--reverse", "--format=COMMIT %H %cI", "-p", "-U0", "--", "docs/INCIDENT-LOG.md")
    for line in log.splitlines():
        if line.startswith("COMMIT "):
            _, h, t = line.split()
            cur = (h, t)
        elif line.startswith("+|") and cur:
            m = re.match(r"^\+\|\s*(?:\*\*)?AF-AP-(\d+)\b", line)
            if m and int(m.group(1)) not in first:
                first[int(m.group(1))] = cur
    return first


def ids_at(rev, paths, ids):
    """{id: [paths]} for the ids found in the given paths at rev (git grep)."""
    if not ids:
        return {}
    pat = r"AF-AP-(" + "|".join(str(i) for i in sorted(ids)) + r")([^0-9]|$)"
    out = git("grep", "-o", "-E", pat, rev, "--", *paths)
    found = collections.defaultdict(set)
    for line in out.splitlines():
        # rev:path:match
        parts = line.split(":", 2)
        if len(parts) == 3:
            m = ID_RX.search(parts[2])
            if m:
                found[int(m.group(1))].add(parts[1])
    return found


def load_events(path):
    ev = []
    for line in open(path):
        e = json.loads(line)
        if e.get("ts"):
            ev.append((ts(e["ts"]), e["kind"], e["cat"], e["name"]))
    ev.sort(key=lambda x: x[0])
    return ev


def window_counts(ev, keys, t0, t1):
    i = bisect.bisect_left(ev, (t0,))
    c = collections.Counter()
    while i < len(ev) and ev[i][0] <= t1:
        _, kind, cat, name = ev[i]
        k = "sub" if kind != "main" else "main"
        for label, pred in keys.items():
            if pred(cat, name):
                c[(label, k)] += 1
        i += 1
    return c


def text_of(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False) if v is not None else ""


def carrier_scan(root, exclude, windows):
    """windows: list of (t0, t1, row, cited ids). Returns {(row, what, kind): count} for hook carriers in each window."""
    res = collections.Counter()
    starts = sorted(w[0] for w in windows)
    lo, hi = starts[0], max(w[1] for w in windows)
    for f in sorted(Path(root).rglob("*.jsonl")):
        if f.name in exclude or f.name == "journal.jsonl":
            continue
        kind = "main" if len(f.relative_to(root).parts) == 2 else "sub"
        with open(f, "rb") as fh:
            for line in fh:
                if (b"hook" not in line and b"is_error" not in line) or b'"timestamp"' not in line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                t = r.get("timestamp")
                if not isinstance(t, str):
                    continue
                tt = ts(t)
                if tt < lo or tt > hi:
                    continue
                texts = []
                if r.get("type") == "attachment" and isinstance(r.get("attachment"), dict):
                    a = r["attachment"]
                    if str(a.get("type", "")).startswith("hook"):
                        texts.append(text_of(a.get("content")) + text_of(a.get("stdout")) + text_of(a.get("stderr")))
                elif r.get("type") == "system" and r.get("subtype") == "stop_hook_summary":
                    texts.append(text_of(r.get("hookErrors")))
                elif r.get("type") == "user" and isinstance(r.get("message"), dict) and isinstance(r["message"].get("content"), list):
                    for b in r["message"]["content"]:
                        if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                            txt = text_of(b.get("content"))
                            if "SEARCH INTERCEPT" in txt or "QUIRK GUARD" in txt:
                                texts.append(txt)
                if not texts:
                    continue
                blob = "\n".join(texts)
                present = {int(x) for x in ID_RX.findall(blob)}
                for (t0, t1, row, cited) in windows:
                    if t0 <= tt <= t1:
                        if "[incident match" in blob:
                            res[(row, "incident-match", kind)] += 1
                        if "EDIT SNAPSHOT" in blob:
                            res[(row, "edit-snapshot", kind)] += 1
                        if cited & present:
                            res[(row, "cited-id-injected", kind)] += 1
    return res


STOP = set("that this with from into when which while where their there then than what each only have been were does done over under after before about also more most same other some such these those they them because would could should every first second third its it's the and for are but not you your".split())


def words(t):
    return {w for w in re.findall(r"[a-z][a-z0-9_-]{3,}", t.lower()) if w not in STOP}


def neighbour(n, R, C):
    """The earlier-recorded row whose mechanism column shares the most words with row n's (Jaccard), as (id, score)."""
    me = words(R[n]["cols"][1] if len(R[n]["cols"]) > 1 else "")
    best = (None, 0.0)
    for k, row in R.items():
        if k == n or k not in C or C[k][1] >= C[n][1]:
            continue
        other = words(row["cols"][1] if len(row["cols"]) > 1 else "")
        if me and other:
            j = len(me & other) / len(me | other)
            if j > best[1]:
                best = (k, j)
    return best


# The project hooks' first record in the /home/user main transcript (scan_transcripts.py hook_first_last, 2026-09-25).
HOOKS_LIVE_MAIN = "2026-09-24T11:06:00+00:00"


def fmt(c, label):
    m, s = c.get((label, "main"), 0), c.get((label, "sub"), 0)
    return f"{m}/{s}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True)
    ap.add_argument("--root", default="/root/.claude/projects")
    ap.add_argument("--exclude", action="append", default=[])
    a = ap.parse_args()
    R = rows()
    C = recording_commits()
    missing = [n for n in range(LO, HI + 1) if n not in R or n not in C]
    if missing:
        sys.exit(f"incidents.py: rows or recording commits missing for {missing}; refusing to print a partial table")
    head = git("rev-parse", "--verify", "HEAD^{commit}").strip()  # resolved once (AF-AP-175)
    print(f"Registry read from the working tree; HEAD {head[:7]}; {len(R)} rows parsed.\n")
    ev = load_events(a.events)
    windows = []
    data = {}
    for n in range(LO, HI + 1):
        h, t = C[n]
        t1 = ts(t)
        t0 = t1 - dt.timedelta(hours=2)
        text = R[n]["text"]
        cited_all = {int(x) for x in ID_RX.findall(text)} - {n}
        cited = {x for x in cited_all if x in C and ts(C[x][1]) < t1}
        later = cited_all - cited
        parent = h + "^"
        screen = ids_at(parent, SCREENS, cited)
        skills = ids_at(parent, [".claude/skills", "CLAUDE.md"], cited)
        own_now = ids_at(head, SCREENS, {n})
        keys = {
            "skill-any": lambda c, nm: c == "skill",
            "ap_screen": lambda c, nm: c == "bash" and nm.endswith("script:ap_screen.py"),
            "jev": lambda c, nm: c == "bash" and (nm.endswith("script:jev_locate.py") or nm.endswith("script:jev_echo.py")),
            "code-instr": lambda c, nm: c == "bash" and ":instr:" in (":" + nm) and "sentrux" not in nm,
            "lane_context": lambda c, nm: c == "bash" and nm.endswith("script:lane_context.sh"),
            "bug-echo": lambda c, nm: c == "skill" and nm == "bug-echo",
        }
        skill_names = sorted({Path(p).parent.name if p.endswith("SKILL.md") else p for ps in skills.values() for p in ps})
        for sk in skill_names:
            keys["skill:" + sk] = (lambda s: (lambda c, nm: c == "skill" and nm == s))(sk)
        wc = window_counts(ev, keys, t0, t1)
        data[n] = dict(h=h[:7], t=t, t0=t0, t1=t1, cited=cited, later=later, screen=screen, skills=skills,
                       skill_names=skill_names, own_now=own_now, wc=wc)
        windows.append((t0, t1, n, cited))
    cs = carrier_scan(a.root, set(a.exclude), windows)

    print("| row | recorded (commit, UTC) | class (the row's mechanism column, first 150 chars) | greppable signature column "
          "(first 60 chars) | earlier rows it cites (recorded before it) | at the parent: screens naming a cited row | "
          "at the parent: skills or CLAUDE.md naming a cited row | 2 h before, main/sub: Skill calls (named skill) | "
          "2 h before, main/sub: ap_screen.py runs, code-instrument runs, lane_context.sh runs, jev runs | 2 h before, "
          "main/sub: [incident match] injections, EDIT SNAPSHOT injections, injections carrying a cited id | a screen "
          "for this row now (HEAD) | project hooks registered in the main session at the commit | nearest earlier row by "
          "word overlap (Jaccard; UNSURE, not a naming) | evidence |")
    print("|" + "---|" * 14)
    summary = collections.Counter()
    for n in range(LO, HI + 1):
        d = data[n]
        cols = R[n]["cols"]
        mech = re.sub(r"\s+", " ", cols[1] if len(cols) > 1 else "")[:150].replace("|", "/")
        sig = re.sub(r"\s+", " ", cols[2] if len(cols) > 2 else "")[:60].replace("|", "/")
        cited = ", ".join(str(x) for x in sorted(d["cited"])) or "none"
        scr = "; ".join(f"{i}: " + ", ".join(sorted(Path(p).name for p in ps)) for i, ps in sorted(d["screen"].items())) or "none"
        sk = "; ".join(f"{i}: " + ", ".join(sorted(Path(p).parent.name if p.endswith("SKILL.md") else p for p in ps))
                       for i, ps in sorted(d["skills"].items())) or "none"
        wc = d["wc"]
        skill_cols = f"any {fmt(wc, 'skill-any')}" + "".join(f"; {s} {fmt(wc, 'skill:' + s)}" for s in d["skill_names"])
        runs = (f"{fmt(wc, 'ap_screen')}, {fmt(wc, 'code-instr')}, {fmt(wc, 'lane_context')}, {fmt(wc, 'jev')}")
        inj = (f"{cs.get((n, 'incident-match', 'main'), 0)}/{cs.get((n, 'incident-match', 'sub'), 0)}, "
               f"{cs.get((n, 'edit-snapshot', 'main'), 0)}/{cs.get((n, 'edit-snapshot', 'sub'), 0)}, "
               f"{cs.get((n, 'cited-id-injected', 'main'), 0)}/{cs.get((n, 'cited-id-injected', 'sub'), 0)}")
        own = ", ".join(sorted(Path(p).name for p in d["own_now"].get(n, []))) or "none"
        # evidence line
        namers = []
        if d["screen"]:
            namers.append("a screen (" + ", ".join(sorted({Path(p).name for ps in d["screen"].values() for p in ps})) + ")")
        if d["skill_names"]:
            namers.append("skill section(s) " + ", ".join(d["skill_names"]))
        if d["cited"]:
            namers.append("earlier row(s) " + ", ".join("AF-AP-" + str(x) for x in sorted(d["cited"])))
        if not namers:
            ev_line = "no instrument, skill section or earlier row named it (by row id)"
            summary["none"] += 1
        else:
            ran = []
            if d["screen"]:
                es = cs.get((n, "edit-snapshot", "main"), 0) + cs.get((n, "edit-snapshot", "sub"), 0)
                aps = wc.get(("ap_screen", "main"), 0) + wc.get(("ap_screen", "sub"), 0)
                ran.append(f"edit-snapshot injected {es}x, ap_screen.py ran {aps}x")
            for s in d["skill_names"]:
                k = wc.get(("skill:" + s, "main"), 0) + wc.get(("skill:" + s, "sub"), 0)
                ran.append(f"{s} loaded {k}x")
            if d["cited"]:
                im = cs.get((n, "incident-match", "main"), 0) + cs.get((n, "incident-match", "sub"), 0)
                ci = cs.get((n, "cited-id-injected", "main"), 0) + cs.get((n, "cited-id-injected", "sub"), 0)
                ran.append(f"[incident match] injected {im}x, a cited id reached the agent through a hook {ci}x")
            ev_line = "named by " + "; ".join(namers) + " — in the 2 h before: " + "; ".join(ran)
            summary["named"] += 1
            if d["screen"]:
                summary["named-by-screen"] += 1
            if d["skill_names"]:
                summary["named-by-skill"] += 1
                if not any(wc.get(("skill:" + s, "main"), 0) + wc.get(("skill:" + s, "sub"), 0) for s in d["skill_names"]):
                    summary["named-by-skill, skill not loaded in window"] += 1
            if d["cited"]:
                summary["cites-earlier-row"] += 1
                if not (cs.get((n, "cited-id-injected", "main"), 0) + cs.get((n, "cited-id-injected", "sub"), 0)):
                    summary["cites-earlier-row, cited id never injected in window"] += 1
        live = "yes" if d["t"] >= HOOKS_LIVE_MAIN else "no"
        summary["hooks registered in main: " + live] += 1
        nb, sc = neighbour(n, R, C)
        nbs = f"AF-AP-{nb} ({sc:.2f})" if nb else "none"
        print(f"| AF-AP-{n} | {d['h']} {d['t'][:16]} | {mech} | {sig} | {cited} | {scr} | {sk} | {skill_cols} | {runs} | "
              f"{inj} | {own} | {live} | {nbs} | {ev_line} |")
    print()
    print("Summary (rows " + str(LO) + "-" + str(HI) + "): " + ", ".join(f"{k} {v}" for k, v in sorted(summary.items())))
    first_t = min(data[n]["t"] for n in data)
    last_t = max(data[n]["t"] for n in data)
    print(f"Recording commits span {first_t} .. {last_t}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
