#!/usr/bin/env python3
"""k2_authoring_probe.py: the coordinator's authoring measurements for the K2 brief (task #353, D-106).

Part A reads the main transcript up to a byte cap, so its counts do not move as the session grows. It splits the
transcript at its compaction boundaries (`"subtype":"compact_boundary"` system records) into context windows and
counts, per window, the distinct tracked project files the main loop touched: through Read, Edit or Write, and through
a Bash command segment whose command word is a reader (cat, head, tail, sed, awk, grep, egrep, rg, less, more, nl, wc,
diff, cmp). Subagent (sidechain) records are left out.

Part B reads the ledger-plane documents at one git revision and counts, per tracked project code file, the lines of
each source that name its path.

The split into command segments is a plain one (on ;, &&, ||, |, newline, $( and backquote); it does not mask quoted
data or heredoc bodies, so Part A's reader counts are an estimate from above. The hook K2 builds uses the System-1
hook's own shell parser instead.

Usage: k2_authoring_probe.py --transcript PATH --bytes N --rev REV
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import statistics
import subprocess
import sys

READERS = {"cat", "head", "tail", "sed", "awk", "grep", "egrep", "rg", "less", "more", "nl", "wc", "diff", "cmp"}
SEGMENT_RX = re.compile(r"\|\||&&|;|\||\n|\$\(|`")
VENDORED = ("sandbox-kit/", ".claude/skills/", ".agents/", "graft/")
CODE_ROOTS = ("scripts/", "src/", "proofs/", "harness-ports/", "tests/", "spikes/")
SOURCES = {"ledger": "todo/BUILD-TASKLIST.md", "decisions": "docs/08_DECISION_LOG.md",
           "incidents": "docs/INCIDENT-LOG.md"}
SKILLS = ("env-tool-quirks", "pc-bridge-lanes", "orchestration", "build-loop", "deep-work", "anti-hollow-green",
          "session-continuity", "code-intel-trio", "ouroboros-stdio")
PREFIXES = ("/home/user/agent-factory/", "./")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def norm(path):
    for pre in PREFIXES:
        if path.startswith(pre):
            return path[len(pre):]
    return path


def pct(vals, q):
    s = sorted(vals)
    return s[int(q * len(s))] if s else 0


def part_a(transcript, cap, tracked):
    project = {f for f in tracked if not f.startswith(VENDORED)}
    windows = [{"rew": set(), "rd": set(), "per_call": []}]
    with open(transcript, "rb") as fh:
        data = fh.read(cap)
    for raw in data.split(b"\n"):
        if b'"compact_boundary"' not in raw and b'"tool_use"' not in raw:
            continue
        try:
            rec = json.loads(raw)
        except ValueError:
            continue                                     # the last line can be cut at the cap
        if rec.get("type") == "system" and rec.get("subtype") == "compact_boundary":
            windows.append({"rew": set(), "rd": set(), "per_call": []})
            continue
        if rec.get("type") != "assistant" or rec.get("isSidechain"):
            continue
        cur = windows[-1]
        for block in rec.get("message", {}).get("content") or []:
            if not (isinstance(block, dict) and block.get("type") == "tool_use"):
                continue
            ti = block.get("input") or {}
            if block.get("name") in ("Read", "Edit", "Write"):
                path = norm(ti.get("file_path") or "")
                if path in project:
                    cur["rew"].add(path)
            elif block.get("name") == "Bash":
                got = set()
                for part in SEGMENT_RX.split(ti.get("command") or ""):
                    try:
                        words = shlex.split(part)
                    except ValueError:
                        words = part.split()
                    while words and "=" in words[0] and not words[0].startswith("-"):
                        words = words[1:]
                    while words and words[0] in ("timeout", "nice", "nohup", "setsid", "time"):
                        words = words[2:] if words[0] == "timeout" else words[1:]
                    if not words or words[0].rsplit("/", 1)[-1] not in READERS:
                        continue
                    got |= {norm(w) for w in words[1:]} & project
                if got:
                    cur["per_call"].append(len(got))
                cur["rd"] |= got
    union = [len(w["rew"] | w["rd"]) for w in windows]
    rew = [len(w["rew"]) for w in windows]
    rd = [len(w["rd"]) for w in windows]
    per_call = [n for w in windows for n in w["per_call"]]
    only_rd = sum(len(w["rd"] - w["rew"]) for w in windows)
    print(f"A windows={len(windows)} bytes={len(data)}")
    print(f"A files per window, Read/Edit/Write: median {statistics.median(rew)} p90 {pct(rew, .9)} max {max(rew)}")
    print(f"A files per window, reader Bash: median {statistics.median(rd)} p90 {pct(rd, .9)} max {max(rd)}")
    print(f"A files per window, the union: median {statistics.median(union)} p90 {pct(union, .9)} max {max(union)}")
    print(f"A share of the union seen only through reader Bash: {only_rd / max(1, sum(union)):.3f}")
    print(f"A files per reader call: median {statistics.median(per_call)} p90 {pct(per_call, .9)} "
          f"max {max(per_call)} calls {len(per_call)}")


def part_b(rev, tracked):
    code = [f for f in tracked if f.startswith(CODE_ROOTS)]
    texts = {k: git("show", f"{rev}:{v}").split("\n") for k, v in SOURCES.items()}
    texts["skills"] = [ln for s in SKILLS for ln in git("show", f"{rev}:.claude/skills/{s}/SKILL.md").split("\n")]
    for key, lines in texts.items():
        print(f"B source {key}: lines {len(lines)} bytes {sum(len(x) + 1 for x in lines)}")
    counts = {key: [sum(1 for ln in lines if f in ln) for f in code] for key, lines in texts.items()}
    print(f"B code files {len(code)}")
    for key, vals in counts.items():
        zero = sum(1 for v in vals if v == 0) / len(vals)
        print(f"B lines naming a file, {key}: median {statistics.median(vals)} p90 {pct(vals, .9)} max {max(vals)} "
              f"none {zero:.2f}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--bytes", type=int, required=True)
    ap.add_argument("--rev", required=True)
    ns = ap.parse_args(argv)
    tracked = set(git("ls-tree", "-r", "--name-only", ns.rev).split("\n")) - {""}
    part_a(ns.transcript, ns.bytes, tracked)
    part_b(ns.rev, tracked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
