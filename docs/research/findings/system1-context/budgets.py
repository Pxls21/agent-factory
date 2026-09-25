#!/usr/bin/env python3
"""budgets.py — S1A evidence demand 4: the size and latency of one call of each instrument a context hook could run.

Each case runs the instrument's CLI the way the code-intel-trio skill and CLAUDE.md spell it, on a real symbol or file
of this repository, N times in a row, and prints one markdown row: stdout bytes (median), an approximate token count
(bytes / 4, a rule of thumb, NOT a tokenizer), rc, wall-clock median / min / max ms, and the 1-minute load average
before and after. The output text stays in memory, except lane_context.sh's pack, which goes to the scratch folder.

Laya (127.0.0.1:47411, the owner's local server): 1 health call and 5 rank calls, each rank with a 1-sentence query and
3 short synthetic chunks; `--venue local` (never the PC bridge) and `--no-log` (nothing written to .jev/). Six requests
in total, under the brief's cap of ten.

Usage: budgets.py --scratch DIR [-n 5] [--lane-n 3]
"""
import argparse
import os
import statistics
import subprocess
import sys
import time

REPO = "/home/user/agent-factory"
CRG = "/root/venv-crg/bin/code-review-graph"
CBM = "/root/.local/bin/codebase-memory-mcp"
SYM = "our_hooks"                                  # scripts/install_session_hooks.py:36
FILE = "scripts/install_session_hooks.py"
QSYM = REPO + "/" + FILE + "::" + SYM              # crg's qualified node id, as lane_context.sh builds it
QUESTION = "who writes the session hooks into the settings file for a session rooted above the repository"
PROMPT_JSON = ('{"hook_event_name":"UserPromptSubmit","prompt":"why did the search intercept hook block the graft ask '
               'call in the pc lane, and which registry row covers the trailing ampersand quirk"}')


def loadavg():
    with open("/proc/loadavg") as fh:
        return fh.read().split()[0]


def run(argv, n, stdin=None, out_file=None):
    times, sizes, rcs = [], [], set()
    la0 = loadavg()
    for _ in range(n):
        t0 = time.perf_counter()
        p = subprocess.run(argv, input=stdin, capture_output=True, cwd=REPO, timeout=600)
        times.append((time.perf_counter() - t0) * 1000)
        size = os.path.getsize(out_file) if out_file and os.path.exists(out_file) else len(p.stdout)
        sizes.append(size)
        rcs.add(p.returncode)
    return times, sizes, rcs, la0, loadavg()


def row(name, cmd, res, n):
    times, sizes, rcs, la0, la1 = res
    b = int(statistics.median(sizes))
    return (f"| {name} | `{cmd}` | {n} | {'/'.join(str(r) for r in sorted(rcs))} | {b} | {b // 4} | "
            f"{statistics.median(times):.0f} | {min(times):.0f} | {max(times):.0f} | {la0} / {la1} |")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--lane-n", type=int, default=3)
    ap.add_argument("--only", default="", help="run only the cases whose name contains this text")
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    pack = os.path.join(a.scratch, "lane-pack.md")
    cases = [
        ("graft ask", ["graft", "ask", QUESTION], f'graft ask "{QUESTION}"', None, None, a.n),
        ("graft skeleton", ["graft", "skeleton", FILE], f"graft skeleton {FILE}", None, None, a.n),
        ("GitNexus impact (CLI)", ["node", ".gitnexus/run.cjs", "impact", SYM, "--direction", "upstream", "--repo", "."],
         f"node .gitnexus/run.cjs impact {SYM} --direction upstream --repo .", None, None, a.n),
        ("GitNexus context (CLI)", ["node", ".gitnexus/run.cjs", "context", SYM, "--repo", "."],
         f"node .gitnexus/run.cjs context {SYM} --repo .", None, None, a.n),
        ("codebase-memory search_graph (CLI)", [CBM, "cli", "search_graph", "--project", "home-user-agent-factory",
                                                "--query", "register session hooks settings file"],
         'codebase-memory-mcp cli search_graph --project home-user-agent-factory --query "register session hooks settings file"',
         None, None, a.n),
        ("code-review-graph callers_of, bare name (replies status ambiguous: 2 nodes match)",
         [CRG, "query", "callers_of", SYM], f"code-review-graph query callers_of {SYM}", None, None, a.n),
        ("code-review-graph callers_of, qualified name (status ok, 3 results)",
         [CRG, "query", "callers_of", QSYM], f"code-review-graph query callers_of {QSYM}", None, None, a.n),
        ("code-review-graph tests_for, qualified name (status ok, 0 results)",
         [CRG, "query", "tests_for", QSYM], f"code-review-graph query tests_for {QSYM}", None, None, a.n),
        ("lane_context.sh on one file", ["bash", "scripts/lane_context.sh", "-q", QUESTION, "-s", SYM, "-o", pack, FILE],
         f'scripts/lane_context.sh -q "<question>" -s {SYM} -o <scratch>/lane-pack.md {FILE}', None, pack, a.lane_n),
        ("wiki-context.py on a sample prompt", ["python3", ".claude/hooks/wiki-context.py"],
         "python3 .claude/hooks/wiki-context.py < <prompt json>", PROMPT_JSON.encode(), None, a.n),
        ("Laya health (local server)", ["python3", "scripts/jev.py", "health", "--venue", "local", "--no-log"],
         "python3 scripts/jev.py health --venue local --no-log", None, None, 1),
        ("Laya rank, 3 chunks (local server)", ["python3", "scripts/jev.py", "rank", "--venue", "local", "--no-log",
                                                "--query", "which hook blocks a grep for an identifier",
                                                "--chunk", "search-intercept answers a semantic grep with graft ask",
                                                "--chunk", "wiki-context injects the live-state block on a prompt",
                                                "--chunk", "turn-retro-gate blocks the turn end once per new HEAD"],
         'python3 scripts/jev.py rank --venue local --no-log --query "<1 sentence>" --chunk <3 short chunks>', None, None, 5),
    ]
    print("| instrument call | command | runs | rc | stdout bytes (median) | ≈ tokens (bytes/4) | median ms | min ms | "
          "max ms | load before / after |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name, argv, shown, stdin, out_file, n in cases:
        if a.only not in name:
            continue
        print(row(name, shown, run(argv, n, stdin, out_file), n), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
