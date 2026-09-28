#!/usr/bin/env python3
"""gate_union.py — the gate's test list: the tests that name each path (scripts/gate_files.py's rule) united with the
tests ripwire's call graph links to the change, each with the runner the project runs it with (task #339, D-103;
LS-B9 round 2 item 1, round 3 F-1, F-2 and F-3).

  python3 scripts/gate_union.py --graph yes|no [--ripwire FILE] [--runner pytest|python3|bash] PATH...
      the run list of one runner (default pytest), sorted: the files the gate hands to that runner
  python3 scripts/gate_union.py --why --graph yes|no [--ripwire FILE] [--mode plan|run] [--max-files N] PATH...
      the headline (the counts), one line per union file with its sources and its runner or why it is not run, a summary

FILE is the saved output of `bash scripts/ripwire_review.sh test-gate P1,P2,...` (the gate stack's `graph` step): an
XML comment, then one `<test-gate ...>` element whose `<t p="..."/>` rows are the tests to run and whose `<u .../>`
rows are the UNTESTED blast radius (ripwire 0.4.0; its --limit caps the `<u>` rows only). Only the rows inside the
`<test-gate>` element are read, never the comment. Two `<test-gate>` elements, or an attribute given twice, is refused
rather than read last-wins (AF-AP-41). A ripwire row naming a file that is gone (a stale index) is left out of the
union and named in --why. With --graph yes, a FILE with no `<test-gate>` element (ripwire unmapped or failed) leaves
the union to gate_files' list and says so in --why; with --graph no, FILE is not read.

Each union file gets one runner, or none and the reason; a file is never dropped silently:
  pytest   a test_*.py or *_test.py outside harness-ports/tests/ (pytest's default python_files; the repo's
           pyproject.toml sets none).
  python3  harness-ports/tests/test_*.py, one process per file: they are scripts, and harness-ports/tests/run-all.sh
           runs each with python3. pytest is the wrong runner for them (VERIFY-LS-B9 F-1, measured): it collects nothing
           from one whose checks sit under __main__, a check() that counts failures never raises under it, and a
           module-level sys.exit stops its whole session, the other files' tests included.
  bash     harness-ports/tests/test_*.sh and run-all.sh, one process per file, as run-all.sh runs them.
  not run  any other file (a fixture module, a support file), and tests/test_vendored_manifest.py, whose whole-file run
           copies about 3.4 GB: its line gives the command for its one relevant test instead.
The --why headline is `run list N of union M: pytest a · python3 b · bash c · not run d`; with --mode run and N over
--max-files it adds ` · REFUSED: ...`, in plan mode ` · over max_files ...`; with N = 0, ` · NOTHING TO RUN: ...`.

exit: 0; 1 with --why when the run list is empty (nothing names the paths, or nothing named is runnable), or with
--mode run when the run list holds more files than --max-files (VERIFY-LS-B9 F-2: 101 files for scripts/stack.py alone,
tests/test_vendored_manifest.py among them); 2 usage, --graph yes with FILE absent, or an ambiguous FILE.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gate_files  # noqa: E402  (the one implementation of "the tests that name a path")

TEST_FILE_RE = re.compile(r"test_.*\.py|.*_test\.py")      # pytest's default python_files, on the basename
GATE_RE = re.compile(r"<test-gate\s([^>]*)>(.*?)</test-gate>", re.S)
ROW_RE = re.compile(r"<t\s[^>]*?\bp=\"([^\"]*)\"")
ATTR_RE = re.compile(r"\b([a-z_]+)=\"([^\"]*)\"")
RUNNERS = ("pytest", "python3", "bash")
HARNESS = "harness-ports/tests/"
MAX_FILES = 40
HEAVY = {      # a test file the gate never runs whole: why, and the command for the part a change needs
    "tests/test_vendored_manifest.py": (
        "a whole-file run copies about 3.4 GB of vendored trees",
        "python3 -m pytest tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation "
        "--basetemp=<a private dir outside every work tree>"),
}


def ripwire_tests(text):
    """(the <t> rows' test paths, the element's attributes); (None, None) when the text holds no <test-gate> element.
    Raises ValueError on two elements or a repeated attribute."""
    found = GATE_RE.findall(text)
    if not found:
        return None, None
    if len(found) > 1:
        raise ValueError("%d <test-gate> elements" % len(found))
    head, body = found[0]
    pairs = ATTR_RE.findall(head)
    keys = [k for k, _ in pairs]
    repeated = sorted({k for k in keys if keys.count(k) > 1})
    if repeated:
        raise ValueError("attribute(s) given twice: %s" % ", ".join(repeated))
    return ROW_RE.findall(body), dict(pairs)


def runner_of(path):
    """(the runner, None) or (None, why the gate does not run the file)."""
    if path in HEAVY:
        why, command = HEAVY[path]
        return None, "%s; run its one relevant test: %s" % (why, command)
    name = os.path.basename(path)
    if path.startswith(HARNESS):
        if "/" not in path[len(HARNESS):] and name.startswith("test_") and name.endswith(".py"):
            return "python3", None
        if "/" not in path[len(HARNESS):] and (name.startswith("test_") and name.endswith(".sh") or name == "run-all.sh"):
            return "bash", None
        return None, "not a harness test (run-all.sh runs harness-ports/tests/test_*.py with python3, test_*.sh with bash)"
    if TEST_FILE_RE.fullmatch(name):
        return "pytest", None
    return None, "not a test file (pytest collects test_*.py and *_test.py; it would import this one and run nothing)"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gate_union.py", description=__doc__.splitlines()[0])
    ap.add_argument("--why", action="store_true", help="the headline, one line per file with its runner, a summary")
    ap.add_argument("--graph", choices=("yes", "no"), required=True, help="whether the graph step ran")
    ap.add_argument("--ripwire", help="the graph step's saved output (read only with --graph yes)")
    ap.add_argument("--runner", choices=RUNNERS, default="pytest", help="the run list printed (without --why)")
    ap.add_argument("--mode", choices=("plan", "run"), default="plan", help="with --why: run refuses a wide run list")
    ap.add_argument("--max-files", type=int, default=MAX_FILES, help="with --why --mode run: the widest run list run")
    ap.add_argument("--root", default=gate_files.ROOT, help="the repository root (default: the one holding this script)")
    ap.add_argument("paths", nargs="+", metavar="PATH")
    a = ap.parse_args(argv)
    if a.max_files < 0:
        ap.error("--max-files must be 0 or more")
    root = os.path.realpath(a.root)
    named = sorted(gate_files.gate(root, a.paths))
    linked, gone, attrs, notes = [], [], {}, []
    if a.graph == "no":
        ripwire = "not run (graph=no)"
    else:
        if not a.ripwire or not os.path.isfile(a.ripwire):
            ap.error("--graph yes needs --ripwire FILE, the graph step's saved output (absent: %s)" % a.ripwire)
        with open(a.ripwire, encoding="utf-8", errors="replace") as fh:
            try:
                rows, attrs = ripwire_tests(fh.read())
            except ValueError as e:
                ap.error("%s: ambiguous ripwire output: %s" % (a.ripwire, e))
        if rows is None:
            ripwire, attrs = "no answer", {}
            notes.append("ripwire gave no <test-gate> element (unmapped or failed): the union is gate_files' list")
        else:
            for p in rows:
                (linked if os.path.isfile(os.path.join(root, p)) else gone).append(p)
            ripwire = str(len(set(linked)))
            if attrs.get("tests_capped", "0") != "0":
                notes.append("ripwire capped its test list (tests_capped=%s): the union may miss tests"
                             % attrs["tests_capped"])
    union = sorted(set(named) | set(linked))
    runs = {p: runner_of(p) for p in union}
    if not a.why:
        for p in union:
            if runs[p][0] == a.runner:
                print(p)
        return 0
    counts = {r: sum(1 for p in union if runs[p][0] == r) for r in RUNNERS}
    n = sum(counts.values())
    headline = "run list %d of union %d: %s · not run %d" % (n, len(union), " · ".join(
        "%s %d" % (r, counts[r]) for r in RUNNERS), len(union) - n)
    refused = n == 0 or (a.mode == "run" and n > a.max_files)
    if n == 0:
        headline += " · NOTHING TO RUN: %s" % ("no test file names these paths" if not union
                                              else "no union file has a runner (see each file's reason)")
    elif n > a.max_files:
        headline += (" · REFUSED: mode=run runs at most max_files=%d files; pass max_files=%d to run these %d"
                     % (a.max_files, n, n) if a.mode == "run" else
                     " · over max_files=%d: mode=run would refuse it; pass max_files=%d to run it" % (a.max_files, n))
    print(headline)
    for p in union:
        src = "+".join(s for s, lst in (("gate_files", named), ("ripwire", linked)) if p in lst)
        runner, why = runs[p]
        print("%s  %s · %s" % (p, src, runner if runner else "not run: " + why))
    for p in sorted(set(gone)):
        print("%s  ripwire, left out: the file is gone (a stale index)" % p)
    summary = "gate_files %d · ripwire %s" % (len(named), ripwire)
    if attrs:
        summary += " · ripwire untested blast radius: %s symbols (%s shown)" % (attrs.get("untested", "?"),
                                                                             attrs.get("shown_untested", "?"))
    print(" · ".join([summary] + notes))
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
