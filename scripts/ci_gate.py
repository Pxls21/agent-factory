#!/usr/bin/env python3
"""ci_gate.py — before a push, read the branch's stage0-ci verdict: refuse while it is red, wait while it is unknown.

Owner, 2026-09-23 ("my email is littered … the third time"): every push onto a red head mails a
"Run failed: stage0-ci" notice. Twice a rule said "read the run before the next push", and twice
the coordinator forgot it (AF-AP-126). push_clean.sh calls this gate after its fetch and before any
rewrite, and the gate enforces the rule: each pushed head's run is read to its conclusion first.

The verdict run R is the newest stage0-ci push run of --branch whose head commit is in the history of the
origin ref (default refs/remotes/origin/<branch>); runs concluded cancelled are skipped. A transcripts-only
push starts no run (the workflow's paths-ignore), so the run of its parent stays the verdict.

  step  condition                                                          exit  note
  a     the clone is shallow                                                 2   names `git fetch --unshallow origin`
  b     the origin ref does not resolve to a commit                          2
  c     --runs-json (a test input) while origin is a github.com remote      64
        the runs cannot be read (the Actions API, or --runs-json)            2   CI_GATE_OFFLINE=<reason>: 0 + WARNING
  d     a record is invalid: a missing key; id or run_number not an int;    2   the API's data: CI_GATE_OFFLINE rescues
        head_sha not 40 lowercase hex; status not a string; conclusion
        not a string or null; head_branch not --branch; event not push;
        a repeated run_number
  e     history, newest run first: merge-base --is-ancestor 0 -> in;         2   when git cannot tell. A local git
        1 with no error line -> out; the commit object absent -> out;            failure (a, b, e) is fixed locally,
        anything else -> git cannot tell                                          never rescued
  f     R is requested / queued / pending / waiting / in_progress           75   wait for R's verdict
        R has any other status, or is completed with no conclusion           2   the API's data: CI_GATE_OFFLINE rescues
        the pushes after R change a path outside transcripts/               75   their run is not registered yet
        R concluded success                                                  0
        CI_FIX equals R's id                                                 0   the push declares it carries the fix
        R concluded anything else                                            1   refused: the verdict is red
  g     no R, and the page is full (50 runs)                                 2   the API's data: CI_GATE_OFFLINE rescues
        no R                                                                 0   with a note
Exit codes: 0 allow · 1 refused, the verdict run is red · 2 cannot decide · 64 usage · 75 wait (EX_TEMPFAIL).
Texts: `ci-gate:` (0, stdout) · `REFUSED by ci-gate:` (1 and 2) · `WAIT by ci-gate:` (75) · `WARNING: ci-gate`
(an override that allowed); all but the first on stderr. Every 75 names the run or the pushes it waits for,
the waiter command and the CI_WAIT_SKIP=<reason> escape. CI_FIX, CI_WAIT_SKIP and CI_GATE_OFFLINE are read
once and stripped; blank means unset. CI_WAIT_SKIP=<reason> turns a 75 into 0 with a WARNING, nothing else.
The runs: GET /repos/<owner>/<repo>/actions/workflows/stage0-ci.yml/runs, the query (branch, event=push,
per_page=50) built by urlencode, timeout 20 s; an HTTP error names its status and X-RateLimit-Remaining.

--wait SECONDS (the waiter; it never fetches and never pushes): the decision every 30 s while it is 75, up to
SECONDS, one line per state change; it returns the final decision (75 at the deadline). A failed read is
retried at the next poll; three in a row -> 2. CI_FIX, CI_WAIT_SKIP and CI_GATE_OFFLINE are ignored (it
reports the run's verdict, not a push decision). On a red verdict it lists the run's failed jobs.
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

WORKFLOW = "stage0-ci.yml"
API = "https://api.github.com"
PER_PAGE = 50
TIMEOUT = 20
POLL_SECONDS = 30
READ_TRIES = 3
USAGE, WAIT = 64, 75
# The workflow ignores IGNORED_PREFIX + "**" on both triggers; tests/test_stage0_ci_workflow.py pins the two equal.
IGNORED_PREFIX = "transcripts/"
UNFINISHED = ("requested", "queued", "pending", "waiting", "in_progress")
KEYS = ("id", "run_number", "head_sha", "status", "conclusion", "head_branch", "event")
OVERRIDES = ("CI_FIX", "CI_WAIT_SKIP", "CI_GATE_OFFLINE")
SHA = re.compile(r"[0-9a-f]{40}")
GITHUB = re.compile(r"(?:^|[/@])github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$")

_sleep, _now = time.sleep, time.monotonic  # the waiter's clock; the tests replace both


class DataError(Exception):
    """The Actions API's data cannot decide: unreadable, invalid or incomplete. CI_GATE_OFFLINE rescues it."""


class GitError(Exception):
    """The local clone cannot answer: shallow, a ref that is no commit, a history read. Fixed locally, never rescued."""


def _git(root, *args):
    """(returncode, stdout, stderr) of one git call, in the C locale so that git's error prefixes are the English ones."""
    try:
        proc = subprocess.run(["git", "-C", root, *args], capture_output=True, env={**os.environ, "LC_ALL": "C"})
    except OSError as exc:
        raise GitError(f"git did not run: {exc}") from None
    return (proc.returncode, proc.stdout.decode("utf-8", "surrogateescape"),
            proc.stderr.decode("utf-8", "surrogateescape"))


def _error_line(stderr):
    return next((line for line in stderr.splitlines() if line.startswith(("error:", "fatal:"))), None)


def check_clone(root):
    """Step a: a shallow clone reads a red run beyond its boundary as outside the history (VERIFY-CI-GATE F1)."""
    rc, out, err = _git(root, "rev-parse", "--is-shallow-repository")
    if rc == 0 and out.strip() == "false":
        return
    if rc == 0 and out.strip() == "true":
        raise GitError("this clone is shallow, so a red run beyond its boundary would read as outside the history. "
                       "Fix it: git fetch --unshallow origin")
    raise GitError(f"git cannot tell whether {root} is a complete clone "
                   f"(rev-parse --is-shallow-repository exited {rc}: {_error_line(err) or out.strip()!r})")


def resolve_commit(root, ref):
    """Step b: the origin ref as a full sha; every later git call reads that sha, never the name again."""
    rc, out, _ = _git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if rc != 0 or not SHA.fullmatch(out.strip()):
        raise GitError(f"the origin ref {ref!r} does not resolve to a commit; fetch it first")
    return out.strip()


def origin_url(root):
    rc, out, _ = _git(root, "remote", "get-url", "origin")
    return out.strip() if rc == 0 else ""


def repo_slug(root):
    url = origin_url(root)
    match = GITHUB.search(url)
    if not match:
        shown = re.sub(r"(?<=://)[^/@]*@", "", url)  # a URL may carry a credential: never print it
        raise DataError(f"origin is not a github.com remote: {shown!r}" if url else "there is no origin remote")
    return f"{match.group(1)}/{match.group(2)}"


def _get_json(url):
    """The JSON body of one GET; every failure is a DataError that names its cause."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        left = exc.headers.get("X-RateLimit-Remaining") if exc.headers is not None else None
        raise DataError(f"{exc}" + (f"; X-RateLimit-Remaining: {left}" if left is not None else "")) from None
    except Exception as exc:  # a URLError, a timeout, a cut connection, a body that is not JSON: all unreadable
        raise DataError(f"{type(exc).__name__}: {exc}") from None


def fetch_runs(repo, branch):
    query = urllib.parse.urlencode({"branch": branch, "event": "push", "per_page": PER_PAGE})
    return _get_json(f"{API}/repos/{repo}/actions/workflows/{WORKFLOW}/runs?{query}")


def fetch_jobs(repo, run_id):
    payload = _get_json(f"{API}/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100")
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(jobs, list):
        raise DataError("the payload carries no jobs list")
    return jobs


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def valid_runs(payload, branch):
    """Step d: payload['workflow_runs'], every record checked before any decision (F6, F7, F19, F22)."""
    runs = payload.get("workflow_runs") if isinstance(payload, dict) else None
    if not isinstance(runs, list):
        raise DataError("the payload carries no workflow_runs list")
    first_at = {}
    for i, run in enumerate(runs):
        name = f"workflow_runs[{i}]"
        if not isinstance(run, dict):
            raise DataError(f"{name} is not an object")
        if _is_int(run.get("id")):
            name += f" (id {run['id']})"
        missing = [key for key in KEYS if key not in run]
        if missing:
            raise DataError(f"{name} has no {missing[0]}")
        for key, ok, wanted in (
                ("id", _is_int(run["id"]), "an integer"),
                ("run_number", _is_int(run["run_number"]), "an integer"),
                ("head_sha", isinstance(run["head_sha"], str) and SHA.fullmatch(run["head_sha"]), "40 lowercase hex"),
                ("status", isinstance(run["status"], str), "a string"),
                ("conclusion", run["conclusion"] is None or isinstance(run["conclusion"], str), "a string or null"),
                ("head_branch", run["head_branch"] == branch, repr(branch)),
                ("event", run["event"] == "push", "'push'")):
            if not ok:
                raise DataError(f"{name}: {key} is {run[key]!r:.80}, not {wanted}")
        at = first_at.setdefault(run["run_number"], i)
        if at != i:
            raise DataError(f"{name}: run_number {run['run_number']} repeats workflow_runs[{at}]")
    return runs


def read_runs(root, branch, runs_json=None):
    """Steps c and d: the validated runs, from the Actions API or the --runs-json test input."""
    if runs_json:
        try:
            with open(runs_json, encoding="utf-8") as fh:
                payload = json.load(fh)
        except Exception as exc:  # a missing file, bytes that are not JSON: unreadable
            raise DataError(f"{type(exc).__name__}: {exc}") from None
    else:
        payload = fetch_runs(repo_slug(root), branch)
    return valid_runs(payload, branch)


def in_history(root, sha, origin_sha):
    """Step e, the tri-state history filter (F1): True, False, or GitError when git cannot tell."""
    rc, _, err = _git(root, "merge-base", "--is-ancestor", sha, origin_sha)
    error = _error_line(err)
    if rc == 0:
        return True
    if rc == 1 and error is None:  # git 2.43 also exits 1 when a walk hits a missing object, but says error:
        return False
    if _git(root, "cat-file", "-e", f"{sha}^{{commit}}")[0] != 0:
        # Absent, so not reachable: sound only because step a refused a shallow clone and step b proved the ref.
        return False
    raise GitError(f"git cannot tell whether commit {sha} is in the history of {origin_sha}: "
                   f"merge-base --is-ancestor exited {rc}" + (f" ({error})" if error else ""))


def first_change_after(root, sha, origin_sha):
    """The first path outside transcripts/ that the pushes after commit `sha` change, or None. --no-renames: a
    rename out of code into transcripts/ shows only its new path by default; -z: raw paths, never quoted ones."""
    rc, out, err = _git(root, "diff", "--no-renames", "--name-only", "-z", sha, origin_sha)
    if rc != 0:
        raise GitError(f"git cannot list the paths changed after {sha}: diff exited {rc} ({_error_line(err)})")
    return next((path for path in out.split("\0") if path and not path.startswith(IGNORED_PREFIX)), None)


def decide(runs, is_ancestor, ci_fix="", change_after=lambda sha: None):
    """(rc, text) for validated runs, steps e-g; DataError when the API's data cannot decide."""
    return _decide(runs, is_ancestor, ci_fix, change_after)[:2]


def _decide(runs, is_ancestor, ci_fix, change_after):
    for run in sorted(runs, key=lambda r: r["run_number"], reverse=True):
        if run["status"] == "completed" and run["conclusion"] == "cancelled":
            continue
        if not is_ancestor(run["head_sha"]):
            continue
        where = f"run #{run['run_number']} ({run['head_sha'][:7]})"
        status, conclusion = run["status"], run["conclusion"]
        if status in UNFINISHED:
            return WAIT, f"WAIT by ci-gate: {where} is {status} — {run.get('html_url', '')}", run
        if status != "completed":
            raise DataError(f"{where} has the status {status!r}: neither completed nor unfinished")
        if conclusion is None:
            raise DataError(f"{where} is completed with no conclusion")
        # The expected-run check: a push starts its run seconds after it lands, so right after a push the newest
        # REGISTERED run is the previous head's. Its verdict is not the pushed code's.
        path = change_after(run["head_sha"])
        if path is not None:
            return WAIT, (f"WAIT by ci-gate: the pushes after {where}, which concluded {conclusion}, change {path} "
                          "and no newer run is registered yet"), run
        if conclusion == "success":
            return 0, f"ci-gate: {where} passed", run
        if ci_fix == str(run["id"]):
            return 0, f"ci-gate: {where} concluded {conclusion}; CI_FIX={ci_fix} declares this push fixes it", run
        return 1, (f"REFUSED by ci-gate: {where} concluded {conclusion} — {run.get('html_url', '')}\n"
                   f"Read its failed jobs first. A push that carries the fix sets CI_FIX={run['id']}."), run
    if len(runs) >= PER_PAGE:
        raise DataError(f"no verdict in the newest {len(runs)} runs: each is cancelled or outside the history, "
                        "and the verdict may be off the page")
    return 0, "ci-gate: no stage0-ci run in this branch's history; nothing to read", None


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # a usage error exits 64, never 2 (2 means "cannot decide"; VERIFY-CI-GATE F8)
        self.print_usage(sys.stderr)
        self.exit(USAGE, f"{self.prog}: error: {message}\n")


def _seconds(text):
    try:
        value = int(text)
    except ValueError:
        value = -1
    if value < 0:
        raise argparse.ArgumentTypeError(f"SECONDS must be a whole number >= 0, not {text!r}")
    return value


def _say(rc, text, err=False):
    print(text, file=sys.stderr if rc or err else sys.stdout)
    return rc


def _body(text):
    return text.splitlines()[0].replace("WAIT by ci-gate: ", "", 1)


def _wait_hint(args, ref):
    cmd = ["python3", "scripts/ci_gate.py", "--branch", args.branch]
    if ref != f"refs/remotes/origin/{args.branch}":
        cmd += ["--origin-ref", ref]
    if args.root != ".":
        cmd += ["--root", args.root]
    if args.runs_json:
        cmd += ["--runs-json", args.runs_json]
    return (f"Wait for the verdict: {shlex.join(cmd + ['--wait', '1800'])}\n"
            "or push without waiting: CI_WAIT_SKIP=<reason>")


def _print_failed_jobs(root, run):
    try:
        jobs = fetch_jobs(repo_slug(root), run["id"])
        lines = [f"  failed job: {job['name']} (id {job['id']})" for job in jobs
                 if job.get("conclusion") not in ("success", "skipped", "neutral", None)]
    except Exception as exc:  # the verdict stands whatever the jobs read does: one warning, the rc stays 1
        print(f"WARNING: ci-gate could not read the failed jobs of run #{run['run_number']} ({exc})", file=sys.stderr)
        return
    print("\n".join(lines) or f"  run #{run['run_number']} lists no failed job", file=sys.stderr)


def _wait(args, verdict, hint):
    """The waiter (C4): the decision every POLL_SECONDS while it is 75, up to args.wait seconds."""
    deadline = _now() + args.wait
    failures, shown = 0, None
    while True:
        try:
            rc, text, run = verdict("")
            failures = 0
        except GitError as exc:
            return _say(2, f"REFUSED by ci-gate: {exc}")
        except DataError as exc:
            failures += 1
            if failures == READ_TRIES or _now() >= deadline:
                return _say(2, f"REFUSED by ci-gate: the runs could not be read ({exc}); "
                               f"{failures} read(s) in a row failed while waiting")
            rc, text = WAIT, f"WAIT by ci-gate: the runs could not be read ({exc}); retry {failures} of {READ_TRIES - 1}"
        if rc != WAIT:
            _say(rc, text)
            if rc == 1:
                _print_failed_jobs(args.root, run)
            return rc
        line = text.splitlines()[0]
        if line != shown:
            print(line, file=sys.stderr)
            shown = line
        remaining = deadline - _now()
        if remaining <= 0:
            return _say(WAIT, f"WAIT by ci-gate: {args.wait} s passed and the verdict is still unknown: "
                              f"{_body(line)}\n{hint}")
        _sleep(min(POLL_SECONDS, remaining))


def main(argv=None):
    ap = _Parser(prog="ci_gate.py", description=__doc__.split("\n")[0])
    ap.add_argument("--branch", required=True)
    ap.add_argument("--origin-ref", help="the fetched ref whose history holds the verdict "
                                         "(default: refs/remotes/origin/<branch>)")
    ap.add_argument("--root", default=".", help="the git work tree")
    ap.add_argument("--runs-json", help="read the runs from this file: a test input, refused when origin is github.com")
    ap.add_argument("--wait", type=_seconds, metavar="SECONDS",
                    help="wait for the verdict: repeat the decision every 30 s while it is 75, up to SECONDS")
    args = ap.parse_args(argv)
    ref = args.origin_ref or f"refs/remotes/origin/{args.branch}"
    ci_fix, wait_skip, offline = (os.environ.get(name, "").strip() for name in OVERRIDES)
    try:
        check_clone(args.root)
        origin_sha = resolve_commit(args.root, ref)
    except GitError as exc:
        return _say(2, f"REFUSED by ci-gate: {exc}")
    if args.runs_json:  # a test input never decides a real push (VERIFY-CI-GATE F5)
        if GITHUB.search(origin_url(args.root)):
            return _say(USAGE, "ci_gate.py: error: --runs-json is a test input and origin is a github.com remote: "
                               "it never decides a real push (unset CI_GATE_RUNS_JSON)")
        print(f"WARNING: ci-gate: runs read from {args.runs_json} (a test input), not the Actions API", file=sys.stderr)

    def verdict(fix):
        runs = read_runs(args.root, args.branch, args.runs_json)
        return _decide(runs, lambda sha: in_history(args.root, sha, origin_sha), fix,
                       lambda sha: first_change_after(args.root, sha, origin_sha))

    hint = _wait_hint(args, ref)
    if args.wait is not None:
        ignored = [f"{name}={value}" for name, value in zip(OVERRIDES, (ci_fix, wait_skip, offline)) if value]
        if ignored:
            print(f"ci-gate: --wait ignores {', '.join(ignored)}: the waiter reports the run's verdict, "
                  "not a push decision", file=sys.stderr)
        return _wait(args, verdict, hint)
    try:
        rc, text, _ = verdict(ci_fix)
    except GitError as exc:
        return _say(2, f"REFUSED by ci-gate: {exc}")
    except DataError as exc:
        if offline:
            return _say(0, f"WARNING: ci-gate could not read the runs ({exc}); pushing anyway: "
                           f"CI_GATE_OFFLINE={offline}", err=True)
        return _say(2, f"REFUSED by ci-gate: the runs could not be read ({exc}). Retry, or set "
                       "CI_GATE_OFFLINE=<reason> to push without the gate.")
    if rc == WAIT and wait_skip:
        return _say(0, f"WARNING: ci-gate did not wait ({_body(text)}); pushing anyway: CI_WAIT_SKIP={wait_skip}",
                    err=True)
    return _say(rc, text + ("\n" + hint if rc == WAIT else ""))


if __name__ == "__main__":
    sys.exit(main())
