#!/usr/bin/env python3
"""ci_gate.py — refuse a push while the branch's last stage0-ci verdict is red (AF-AP-126).

Owner, 2026-09-23 ("my email is littered … the third time"): every push onto a red head mails a
"Run failed: stage0-ci" notice. Twice a rule said "read the run before the next push", and twice
the coordinator forgot it. push_clean.sh now calls this gate after its fetch and before any rewrite.

The verdict is the newest stage0-ci push run on the branch whose head commit is in the history of
the origin ref (a transcripts-only push has no run of its own; its parent's run is the verdict):
  completed/success          -> allow
  queued / in_progress       -> allow (this push supersedes it; the workflow's concurrency cancels it)
  completed/cancelled        -> skip it and read the next older run (a newer push superseded it)
  any other completed result -> REFUSE, unless CI_FIX names that run's id: the push declares that
                                it carries the fix, and the id can only come from reading the run
  no run in the history      -> allow, with a note
Exit codes: 0 allow, 1 refused, 2 the runs could not be read (fail closed; CI_GATE_OFFLINE=<reason>
turns that one case into a loud warning), 64 usage.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request

WORKFLOW = "stage0-ci.yml"
API = "https://api.github.com"


def decide(runs, is_ancestor, ci_fix=""):
    """(rc, message) for the newest non-cancelled run whose head commit is in the history."""
    for run in sorted(runs, key=lambda r: r["run_number"], reverse=True):
        if not is_ancestor(run["head_sha"]):
            continue
        where = f"run #{run['run_number']} ({run['head_sha'][:7]})"
        if run["status"] != "completed":
            return 0, f"ci-gate: {where} is {run['status']}; this push supersedes it"
        if run["conclusion"] == "cancelled":
            continue
        if run["conclusion"] == "success":
            return 0, f"ci-gate: {where} passed"
        if ci_fix == str(run["id"]):
            return 0, f"ci-gate: {where} concluded {run['conclusion']}; CI_FIX={ci_fix} declares this push fixes it"
        return 1, (f"REFUSED by ci-gate: {where} concluded {run['conclusion']} — {run.get('html_url', '')}\n"
                   f"Read its failed jobs first. A push that carries the fix sets CI_FIX={run['id']}.")
    return 0, "ci-gate: no stage0-ci run in this branch's history; nothing to read"


def repo_slug(root):
    url = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"],
                         capture_output=True, text=True, check=True).stdout.strip()
    m = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not m:
        raise ValueError(f"origin is not a github.com remote: {url!r}")
    return f"{m.group(1)}/{m.group(2)}"


def fetch_runs(repo, branch):
    url = f"{API}/repos/{repo}/actions/workflows/{WORKFLOW}/runs?branch={branch}&event=push&per_page=50"
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.load(resp)["workflow_runs"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--branch", required=True)
    ap.add_argument("--origin-ref", required=True, help="the fetched ref whose history holds the verdict")
    ap.add_argument("--root", default=".", help="the git work tree")
    ap.add_argument("--runs-json", help="read the runs from this file (a test input) instead of the Actions API")
    args = ap.parse_args(argv)

    def is_ancestor(sha):
        return subprocess.run(["git", "-C", args.root, "merge-base", "--is-ancestor", sha, args.origin_ref],
                              capture_output=True).returncode == 0

    try:
        if args.runs_json:
            print(f"ci-gate: runs read from {args.runs_json} (a test input), not the Actions API")
            with open(args.runs_json, encoding="utf-8") as fh:
                runs = json.load(fh)["workflow_runs"]
        else:
            runs = fetch_runs(repo_slug(args.root), args.branch)
    except Exception as exc:  # every read failure is the same verdict: unknown
        offline = os.environ.get("CI_GATE_OFFLINE", "").strip()
        if offline:
            print(f"WARNING: ci-gate could not read the runs ({exc}); pushing anyway: CI_GATE_OFFLINE={offline}",
                  file=sys.stderr)
            return 0
        print(f"REFUSED by ci-gate: the runs could not be read ({exc}). Retry, or set "
              "CI_GATE_OFFLINE=<reason> to push without the gate.", file=sys.stderr)
        return 2

    rc, message = decide(runs, is_ancestor, os.environ.get("CI_FIX", "").strip())
    print(message, file=sys.stderr if rc else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main())
