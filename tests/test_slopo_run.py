"""SLOPO2 (task #285): scripts/slopo_run.py runs slopo's own CLI with a walker that never enters a directory the config
excludes whole, in place of slopo's whole-tree scan (tasks/briefs/system1/SLOPO2-brief.md).

Deterministic and LLM-free. pytest runs on 3.11 here, which cannot import slopo: a DRIVER runs in the slopo venv's
python (3.12, as in the sandbox) or in /usr/bin/python3.13 (the PC venv's interpreter family; stdlib-only parts), fed
a JSON request on stdin. Where either interpreter is absent (CI has no slopo venv) those tests SKIP with the reason.
  1. the walk order: rglob_entries equals CPython's own Path.rglob("*"), entry for entry, on 3.12 and on 3.13, with
     and without pruning, on a tree holding symlinks (to a directory, a file, nowhere), hidden entries, a directory
     named like a file and mixed case; the other interpreter's order does NOT match (the tree tells them apart);
  2. equality with slopo's own scanner (same paths, same order) on this repository (skipped, with the reason, on a
     tree past TREE_BUDGET entries, where slopo's own walk takes minutes: the PC's) and on trees built to break a
     pruning walker; for each, a walker that prunes ONE directory too many fails (the negative control);
  3. the pruning prunes: every os.scandir call recorded; the walker lists nothing inside a large excluded directory,
     while slopo's scan and an unpruned walk (the controls: the recorder sees such reads) list all of it;
  4. the pruning rule reads the config's regexes the same way on 3.12 and 3.13;
  5. the seam checks: a wrong pinned version, a foreign scan_directory, a sync_index that no longer calls it, a scanner
     whose code changed, an unknown interpreter: each runs slopo unchanged and names the check in one stderr line;
     a rule that pathspec contradicts makes the walker fall back to slopo's own scan;
  6. end to end: bin/slopo and the launcher index one tree into two databases with the same rows in the same order
     (a flipped walk order does not), and the launcher exits with slopo's code;
  7. --compare: exit 0 on equal lists; 1 on a missing directory, another order or a rule disagreement; 2 on usage
     or a config slopo refuses; 3 on a failed seam check.
"""
import json
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LAUNCHER = SCRIPTS / "slopo_run.py"
CONFIG = ROOT / "slopo.conf.yaml"
VENV = Path(os.environ.get("SLOPO_VENV", str(Path.home() / "venv-slopo")))
SLOPO_PY = VENV / "bin" / "python"
SLOPO_BIN = VENV / "bin" / "slopo"
PY313 = Path("/usr/bin/python3.13")


def present(path):
    """A venue probe that never raises: under another identity a stat can refuse (AF-AP-44)."""
    try:
        return path.is_file()
    except OSError:
        return False


HAVE_SLOPO = present(SLOPO_BIN) and present(SLOPO_PY)
needs_slopo = pytest.mark.skipif(not HAVE_SLOPO, reason="no slopo venv at %s (scripts/setup.sh builds it)" % VENV)
needs_313 = pytest.mark.skipif(not present(PY313), reason="no /usr/bin/python3.13 (the PC venv's interpreter family)")
REAL_EXCLUDE = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["source_dir_exclude"]
# Past this many entries slopo's own walk of the repository takes minutes (the PC's ~20 million: 20 minutes), so the
# on-this-repository test skips there; `scripts/slopo_run.py --compare` is that venue's check (the SLOPO2 report).
TREE_BUDGET = 200_000
BODY = "def unit(items):\n    total = 0\n    for item in items:\n        total += item\n    return total\n"

DRIVER = r'''
import json, os, sys
from pathlib import Path

req = json.loads(sys.stdin.read())
sys.path.insert(0, req["scripts"])
import slopo_run as r


def recorded(fn):
    """(fn(), every path os.scandir was called with while fn ran)."""
    seen, real = [], os.scandir
    def rec(p):
        seen.append(os.fspath(p))
        return real(p)
    os.scandir = rec
    try:
        return fn(), seen
    finally:
        os.scandir = real


def too_many(victim):
    """The walker's own pruning rule, plus ONE directory it must not prune."""
    class TooMany(r.Pruner):
        def __call__(self, rel):
            return rel == victim or super().__call__(rel)
    return TooMany


def rel_in(paths, root, rel):
    """How many of paths lie at or below root/rel."""
    base = os.path.join(root, rel) if root not in (".", "") else rel
    return sum(1 for p in paths if p == base or p.startswith(base + "/"))


def apply(patches):
    calls = {"foreign": 0}
    for p in patches:
        if p == "flip-lifo":
            r.LIFO_BY_INTERPRETER = {k: not v for k, v in r.LIFO_BY_INTERPRETER.items()}
        elif p == "wrong-prefix":
            r._anchored_prefix = lambda items, c: "zzz/"
        elif p.startswith("too-many:"):
            walk, factory = r.walk_paths, too_many(p.split(":", 1)[1])
            r.walk_paths = lambda root, exclude, stats=None: walk(root, exclude, stats, prune_factory=factory)
        elif p == "foreign-scan":
            import slopo.indexing.sync as sync
            orig = sync.scan_directory
            def scan_directory(root, exclude):
                calls["foreign"] += 1
                return orig(root, exclude)
            sync.scan_directory = scan_directory
        elif p == "sync-index-renamed":
            import slopo.indexing.sync as sync
            inner = sync.sync_index
            def sync_index(*a, **k):
                return inner(*a, **k)
            sync.sync_index = sync_index
        elif p == "changed-scanner":
            import slopo.indexing.scanner as scanner
            import slopo.indexing.sync as sync
            orig = scanner.scan_directory
            def scan_directory(root, exclude):
                return iter(sorted(orig(root, exclude)))
            scan_directory.__module__ = "slopo.indexing.scanner"
            scanner.scan_directory = sync.scan_directory = scan_directory
        else:
            raise SystemExit("unknown patch %r" % p)
    return calls


op = req["op"]
out = {}
calls = apply(req.get("patches", []))
if req.get("cwd"):
    os.chdir(req["cwd"])
if op == "order":
    root = Path(req["root"])
    pruned = set(req.get("prune", []))
    prune = lambda rel: rel in pruned
    lifo = r.LIFO_BY_INTERPRETER[sys.version_info[:2]]
    keep = lambda p: not any(os.path.relpath(p, root).startswith(d + "/") for d in pruned)
    out["rglob"] = [str(p) for p in root.rglob("*") if keep(p)]
    out["walker"] = [str(p) for p in r.rglob_entries(root, prune, lifo)]
    out["other"] = [str(p) for p in r.rglob_entries(root, prune, not lifo)]
    out["python"] = "%d.%d" % sys.version_info[:2]
elif op == "rule":
    import re
    res = []
    for s in req["regexes"]:
        t = r._tree(re.compile(s))
        res.append(None if t is None else [r._monotone(*t), r._anchored_prefix(*t)])
    out["rule"] = res
elif op == "equal":
    import slopo.indexing.scanner as scanner
    root, exclude = Path(req["root"]), req["exclude"]
    out["slopo"] = list(scanner.scan_directory(root, exclude))
    stats = {"listed": 0, "pruned": []}
    out["walker"], reads = recorded(lambda: r.walk_paths(root, exclude, stats))
    out["slopo2"] = list(scanner.scan_directory(root, exclude))
    out["pruned"], out["listed"] = stats["pruned"], stats["listed"]
    out["read_git"] = rel_in(reads, req["root"], ".git")
    victim = next((p.rsplit("/", 1)[0] for p in out["walker"] if "/" in p), None)
    out["victim"] = victim
    out["mutant"] = r.walk_paths(root, exclude, prune_factory=too_many(victim)) if victim else None
elif op == "reads":
    import slopo.indexing.scanner as scanner
    root, exclude, under = Path(req["root"]), req["exclude"], req["under"]
    walker, wr = recorded(lambda: r.walk_paths(root, exclude))
    slopo, sr = recorded(lambda: list(scanner.scan_directory(root, exclude)))
    class Off(r.Pruner):
        def __call__(self, rel):
            return False
    unpruned, ur = recorded(lambda: r.walk_paths(root, exclude, prune_factory=Off))
    out.update(equal=walker == slopo == unpruned, n=len(walker), walker_under=rel_in(wr, req["root"], under),
               slopo_under=rel_in(sr, req["root"], under), unpruned_under=rel_in(ur, req["root"], under),
               walker_reads=len(wr), slopo_reads=len(sr))
elif op == "seam":
    out["problem"] = r.seam_problem(tuple(req["version_info"]) if req.get("version_info") else None)
elif op in ("launch", "compare"):
    import slopo.indexing.sync as sync
    try:
        rc = r.main(req["argv"]) if op == "launch" else r.compare(req["argv"])
    except SystemExit as e:
        rc = e.code
    out["rc"] = rc
    out["installed"] = getattr(sync.scan_directory, "__module__", None) == "slopo_run"
    out["foreign_calls"] = calls["foreign"]
sys.stdout.flush()
print("DRIVER-RESULT " + json.dumps(out))
'''


def drive(req, python=SLOPO_PY, scripts=SCRIPTS):
    """Run DRIVER under `python`; returns (result dict, the completed process)."""
    req = {"scripts": str(scripts), **req}
    p = subprocess.run([str(python), "-c", DRIVER], input=json.dumps(req), capture_output=True, text=True, timeout=300,
                       env={**os.environ, "LITELLM_LOCAL_MODEL_COST_MAP": "True"})
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith("DRIVER-RESULT ")]
    assert lines, "driver failed (rc %s):\n%s\n%s" % (p.returncode, p.stdout[-3000:], p.stderr[-3000:])
    return json.loads(lines[-1][len("DRIVER-RESULT "):]), p


def build(root, files=(), dirs=(), links=()):
    """A tree under root: files (each a small function slopo would index), empty dirs, and (name, target) symlinks."""
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
    for f in files:
        (root / f).parent.mkdir(parents=True, exist_ok=True)
        (root / f).write_text(BODY)
    for name, target in links:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, root / name)
    return root


def conf(tmp_path, exclude=None, name="conf"):
    """A slopo config of slopo's own format with its own database under tmp_path (never slopo.db): the real config's
    model settings, source_dir "." and `exclude` (None: the real config's list)."""
    raw = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    raw.update(source_dir=".", db_file=str(tmp_path / (name + ".db")), report_dir=str(tmp_path / (name + "-report")),
               ignore_file=str(tmp_path / (name + "-ignore.txt")))
    if exclude is not None:
        raw["source_dir_exclude"] = exclude
    path = tmp_path / (name + ".yaml")
    path.write_text(yaml.safe_dump(raw, sort_keys=False))
    return path


def lock_root(tmp_path, version):
    """A copy of the launcher under <root>/scripts with its own upstream.lock.yaml pinning `version`: the launcher
    reads the lock beside its own repository root. Returns the copy's scripts dir."""
    root = tmp_path / "lockroot"
    (root / "scripts").mkdir(parents=True)
    shutil.copy2(LAUNCHER, root / "scripts" / LAUNCHER.name)
    (root / "upstream.lock.yaml").write_text(yaml.safe_dump({"advisory_tooling": {"slopo": {"version": version}}}))
    return root / "scripts"


def slopo_run_lines(stderr):
    return [ln for ln in stderr.splitlines() if ln.startswith("slopo_run")]


# ---------- 1. the walk order, against CPython's own rglob ----------

ORDER_FILES = ["top.py", ".dot.py", "Mixed.PY", "a/1.py", "a/x/2.py", "a/x/deep/3.py", "a/y/4.PY", "b/5.py",
               "b/z/6.py", "b/z/w/7.py", "b/.hid/8.py", ".h/q/9.py", "c/x.py/10.py"]
ORDER_LINKS = [("link_dir", "a"), ("link_file.py", "b/5.py"), ("dangling.py", "nowhere"), ("b/up", "..")]


def order_tree(tmp_path):
    # a and b each hold subdirectories with files: whatever order scandir lists them in, 3.12 (first child first)
    # and 3.13 (last child first) emit a/x/* and b/z/* in opposite orders, so the tree tells the two apart
    return build(tmp_path / "t", ORDER_FILES, links=ORDER_LINKS)


@pytest.mark.parametrize("python", [
    pytest.param(SLOPO_PY, marks=needs_slopo, id="slopo-venv"),
    pytest.param(PY313, marks=needs_313, id="3.13")])
@pytest.mark.parametrize("prune", [[], ["b"], ["a/x", ".h"]], ids=["unpruned", "prune-b", "prune-a-x-and-.h"])
def test_walk_order_is_rglob_order(tmp_path, python, prune):
    root = order_tree(tmp_path)
    res, _ = drive({"op": "order", "root": str(root), "prune": prune}, python=python)
    assert res["walker"] == res["rglob"], res["python"]
    assert len(res["rglob"]) >= 12 and any(p.endswith("/link_dir") for p in res["rglob"])   # the oracle acted
    assert not any("/link_dir/" in p or "/up/" in p for p in res["rglob"])     # rglob never enters a symlinked dir
    assert res["other"] != res["rglob"]          # the negative control: the other interpreter's order is wrong here


# ---------- 2. equality with slopo's own scanner ----------

CASES = {   # name: (exclude lines, None = slopo.conf.yaml's; files; symlinks; the directories the walker must prune)
    # a negation that brings back a deep directory under an excluded one
    "deep-negation": (["/*", "/*/", "!/a/b/c/d/"],
                      ["top.py", "a/drop.py", "a/b/c/drop.py", "a/b/other/drop.py", "a/b/c/d/keep.py",
                       "a/b/c/d/e/keep2.py", "z/drop.py"], [], ["a/b/other", "z"]),
    # an unanchored negation: any directory may hold a brought-back name, so nothing is pruned
    "unanchored-negation": (["/*/", "!keep.py"],
                            ["top.py", "deep/x/y/keep.py", "deep/x/drop.py", "other/keep.py", ".hidden/keep.py"], [],
                            []),
    # a **/ exclude inside a brought-back root
    "doublestar-in-root": (["/*", "/*/", "!/src/", "**/gen/"],
                           ["src/ok.py", "src/gen/drop.py", "src/x/gen/drop.py", "src/x/ok2.py", "src/generated/ok3.py",
                            "lib/gen/drop.py"], [], ["lib", "src/gen", "src/x/gen"]),
    # an excluded directory holding a brought-back directory: its sibling is pruned, the path to it is not
    "excluded-dir-anchored-bring-back": (["/*", "/*/", "!/src/", "**/vendor/", "!/src/vendor/keep/"],
                                         ["src/ok.py", "src/vendor/drop.py", "src/vendor/keep/k.py",
                                          "src/vendor/deep/drop.py", "src/vendor/deep/keep.py", "lib/vendor/keep/x.py"],
                                         [], ["lib", "src/vendor/deep"]),
    # an excluded directory holding a brought-back file name, unanchored: nothing can be pruned
    "excluded-dir-unanchored-bring-back": (["/*", "/*/", "!/src/", "**/vendor/", "!keep.py"],
                                           ["src/ok.py", "src/vendor/drop.py", "src/vendor/keep.py",
                                            "src/vendor/deep/keep.py", "src/vendor/deep/drop.py", "lib/keep.py"], [],
                                           []),
    # files at the root, beside a brought-back directory
    "root-files": (["/*/", "!/keep/"], ["top.py", ".dot.py", "keep/k.py", "other/o.py"], [], ["other"]),
    # "/*" alone excludes root entries, never what lies below them (its regex has an end anchor: no pruning)
    "root-star-only": (["/*"], ["top.py", "a/x.py", "a/b/y.py"], [], []),
    # hidden files and directories
    "hidden": (["/*/", "!/.h/", "/.h/.inner/"],
               [".top.py", ".h/a.py", ".h/.inner/b.py", ".h/.x/c.py", ".other/d.py", "a/.hid.py"], [],
               [".h/.inner", ".other", "a"]),
    # symlinks to a directory, to a file, to nowhere, and out of the root into an excluded directory
    "symlinks": (["/*", "/*/", "!/src/"],
                 ["src/real/r.py", "outside/o.py"],
                 [("src/link_dir", "real"), ("src/link.py", "real/r.py"), ("src/dangling.py", "nowhere"),
                  ("src/link_out.py", "../outside/o.py"), ("root_link", "src")], ["outside"]),
    # a directory named like a file pattern: "/src/mod.py" also excludes everything below a directory of that name
    "dir-named-like-file": (["/*", "/*/", "!/src/", "/src/mod.py", "!/src/mod.py/keep.py"],
                            ["src/ok.py", "src/mod.py/inner.py", "src/mod.py/deep/x.py", "src/mod.py/keep.py"], [], []),
    # mixed-case extensions, a case-sensitive pattern, a directory that differs from a root in case only
    "mixed-case": (["/*", "/*/", "!/src/", "*.py"],
                   ["src/X.PY", "src/y.Rs", "src/z.TS", "src/w.py", "src/sub/V.Py", "SRC/a.py"], [], ["SRC"]),
    # regex metacharacters and a space in names
    "metachars": (["/*", "/*/", "!/a+b/", "!/e.f/", "!/c d/"],
                  ["a+b/x.py", "aab/x.py", "e.f/x.py", "eXf/x.py", "c d/x.py", "cd/x.py"], [], ["aab", "cd", "eXf"]),
    # a wildcard inside a negation: its literal prefix is "sa"
    "wildcard-negation": (["/*", "/*/", "!/sa*/keep/"],
                          ["sandbox/keep/k.py", "sa/keep/k2.py", "sb/keep/k3.py", "sandbox/other/o.py"], [], ["sb"]),
    # a negation before the exclude it would override: the later exclude wins
    "negation-first": (["!/src/", "/*/", "!/src/keep/"], ["src/other/o.py", "src/o2.py", "src/keep/k.py", "top.py"], [],
                       ["src/other"]),
    # non-ASCII names
    "unicode": (["/*", "/*/", "!/\u00fcn\u00ef/"], ["\u00fcn\u00ef/x.py", "uni/x.py"], [], ["uni"]),
    # "*" and a negation that no directory can rule out
    "star-and-py": (["*", "!*.py"], ["a/b/x.py", "a/x.rs", "y.py"], [], []),
    # the real config over the PC's shape: .lanes/ and .suite/ hold the bulk
    "pc-shape": (None,
                 [".lanes/l1/deep/x.py", ".lanes/l2/y.py", ".suite/s/y.py", ".git/hooks/h.py", "scripts/a.py",
                  "scripts/hooks/h.py", "scripts/vendor/v.py", "src/agent_factory/m.py",
                  "proofs/S0-01/tools/archive/old.py", "proofs/S0-01/tools/new.py", "proofs/S0-01/vendor/acp.rs",
                  "harness-ports/bin/x.ts", "tests/test_x.py", "top.py", "sandbox-kit/k.py", "scripts2/nope.py"], [],
                 [".git", ".lanes", ".suite", "proofs/S0-01/tools/archive", "proofs/S0-01/vendor", "sandbox-kit",
                  "scripts/vendor", "scripts2", "tests"]),
}


@needs_slopo
@pytest.mark.parametrize("case", sorted(CASES))
def test_walker_equals_slopo_scanner(tmp_path, case):
    exclude, files, links, pruned = CASES[case]
    exclude = REAL_EXCLUDE if exclude is None else exclude
    root = build(tmp_path / "t", files, links=links)
    res, _ = drive({"op": "equal", "root": str(root), "exclude": exclude})
    assert res["walker"] == res["slopo"]                        # same paths, same order
    assert any("/" in p for p in res["slopo"]), res["slopo"]    # the oracle acted, below the root too
    assert sorted(res["pruned"]) == pruned                      # and the walker pruned what the rule allows, no less
    victim = res["victim"]
    lost = [p for p in res["slopo"] if p.startswith(victim + "/")]
    assert lost and res["mutant"] == [p for p in res["slopo"] if p not in lost]   # one directory too many: red


def tree_larger_than(root, budget):
    """True as soon as a walk of root has seen more than `budget` entries: the probe's cost is bounded by the budget."""
    seen = 0
    for _, dirs, files in os.walk(root):
        seen += len(dirs) + len(files)
        if seen > budget:
            return True
    return False


def test_tree_probe_stops_at_its_budget(tmp_path):
    build(tmp_path, ["a/b/c.py", "a/d.py", "e.py"])              # 5 entries: a, e.py, a/b, a/d.py, a/b/c.py
    assert tree_larger_than(tmp_path, 4) and not tree_larger_than(tmp_path, 5)


@needs_slopo
def test_walker_equals_slopo_scanner_on_this_repository():
    if tree_larger_than(ROOT, TREE_BUDGET):
        pytest.skip("this tree holds more than %d entries: slopo's own walk takes minutes here (the PC: 20 minutes);"
                    " run `scripts/slopo_run.py --compare` on this venue instead" % TREE_BUDGET)
    for _ in range(3):                           # lanes write into this tree: a scan that moved under us is retried
        res, _ = drive({"op": "equal", "root": ".", "exclude": REAL_EXCLUDE, "cwd": str(ROOT)})
        if res["slopo"] == res["slopo2"]:
            break
    else:
        pytest.fail("the tree kept moving between two scans of slopo's")
    assert res["walker"] == res["slopo"] and len(res["slopo"]) >= 100
    if (ROOT / ".git").is_dir():                 # a clone; in a linked worktree .git is a one-line file, nothing to prune
        assert ".git" in res["pruned"]
    assert res["read_git"] == 0                  # it never listed .git
    lost = [p for p in res["slopo"] if p.startswith(res["victim"] + "/")]
    assert lost and res["mutant"] == [p for p in res["slopo"] if p not in lost]


# ---------- 3. the pruning prunes ----------

@needs_slopo
def test_the_walker_reads_nothing_inside_a_large_excluded_directory(tmp_path):
    files = ["scripts/a.py", "src/m.py"] + ["big/d%02d/e%02d/f%d.py" % (i, j, k)
                                            for i in range(20) for j in range(10) for k in range(5)]
    root = build(tmp_path / "t", files)
    res, _ = drive({"op": "reads", "root": str(root), "exclude": REAL_EXCLUDE, "under": "big"})
    assert res["equal"] and res["n"] == 2                  # all three walks give slopo's list
    assert res["walker_under"] == 0                         # the walker listed nothing in big/
    # the controls: the same recorder sees slopo's rglob and an unpruned walk list every directory of big/ (221)
    assert res["slopo_under"] >= 221 and res["unpruned_under"] >= 221
    assert res["walker_reads"] < res["slopo_reads"]


# ---------- 4. the rule reads the config's regexes alike on both interpreters ----------

RULE_EXPECTED = {                                # pathspec 1.1.1's regex for each line of slopo.conf.yaml
    "/*": ("^[^/]+/?$", [False, ""]),
    "/*/": ("^[^/]+/", [True, ""]),
    "!/scripts/": ("^scripts/", [True, "scripts/"]),
    "!/src/": ("^src/", [True, "src/"]),
    "!/proofs/": ("^proofs/", [True, "proofs/"]),
    "!/harness-ports/": ("^harness\\-ports/", [True, "harness-ports/"]),
    "**/vendor/": ("^(?:.+/)?vendor/", [True, ""]),
    "/proofs/S0-01/tools/archive/": ("^proofs/S0\\-01/tools/archive/", [True, "proofs/S0-01/tools/archive/"]),
}
RULE_EXTRA = ["^(?:.+/)?keep\\.py(?:/|$)", ".", "(?i)^scripts/", "^a(?=b)", "^scripts|src"]


@needs_slopo
@needs_313
def test_the_rule_reads_the_config_s_regexes_alike_on_3_12_and_3_13():
    got = yaml.safe_load(subprocess.run(
        [str(SLOPO_PY), "-c", "import json, sys, yaml; from pathspec import PathSpec; lines = yaml.safe_load(open("
         "sys.argv[1]))['source_dir_exclude']; print(json.dumps({p.pattern: p.regex.pattern for p in "
         "PathSpec.from_lines('gitignore', lines).patterns}))", str(CONFIG)],
        capture_output=True, text=True, timeout=60, check=True).stdout)
    assert got == {k: v[0] for k, v in RULE_EXPECTED.items()}   # the regexes the rule was written against
    regexes = list(got.values()) + RULE_EXTRA
    a, _ = drive({"op": "rule", "regexes": regexes})
    b, _ = drive({"op": "rule", "regexes": regexes}, python=PY313)
    assert a["rule"] == b["rule"]
    assert a["rule"][:len(got)] == [v[1] for v in RULE_EXPECTED.values()]
    # an end anchor or a lookahead is not monotone; "." and a top-level branch with an unanchored arm have no prefix
    # (they can match anywhere); a flag makes the regex unreadable
    assert a["rule"][len(got):] == [[False, ""], [True, None], None, [False, "a"], [True, None]]


# ---------- 5. the seam checks ----------

@needs_slopo
def test_seam_checks_pass_on_the_pinned_install():
    res, _ = drive({"op": "seam"})
    assert res["problem"] is None


@needs_slopo
@pytest.mark.parametrize("version_info", [[3, 14], [3, 11]])
def test_seam_check_refuses_an_interpreter_whose_order_is_unmeasured(version_info):
    res, _ = drive({"op": "seam", "version_info": version_info})
    assert res["problem"] == ("seam check 'interpreter' failed (Python %d.%d; the walker knows rglob's order on 3.12"
                              " and 3.13)" % tuple(version_info))


def seam_tree(tmp_path):
    return build(tmp_path / "t", ["src/a.py", "big/x/y.py", "top.py"])


@needs_slopo
def test_wrong_pinned_version_runs_slopo_unchanged_and_says_so(tmp_path):
    root = seam_tree(tmp_path)
    scripts = lock_root(tmp_path, "0.0.0")
    c = conf(tmp_path, ["/*", "/*/", "!/src/"])
    res, p = drive({"op": "launch", "argv": ["--config", str(c), "index"], "cwd": str(root)}, scripts=scripts)
    assert res["rc"] == 0 and not res["installed"]
    assert slopo_run_lines(p.stderr) == ["slopo_run: seam check 'version' failed (installed slopo 0.6.0, "
                                         "upstream.lock.yaml pins 0.0.0); running slopo unchanged"]
    assert "Indexed 1 code units from 1 files" in p.stdout
    ok, p2 = drive({"op": "launch", "argv": ["--config", str(conf(tmp_path, ["/*", "/*/", "!/src/"], "c2")), "index"],
                    "cwd": str(root)})
    assert ok["rc"] == 0 and ok["installed"] and slopo_run_lines(p2.stderr) == []   # the control: the real lock
    assert "Indexed 1 code units from 1 files" in p2.stdout


@needs_slopo
@pytest.mark.parametrize("patch,detail", [
    ("foreign-scan", "slopo.indexing.sync.scan_directory is <function apply.<locals>.scan_directory at "),
    ("changed-scanner", "scan_directory's code no longer names ['*', 'PathSpec', 'as_posix', 'from_lines', "
                        "'gitignore', 'is_file', 'lower', 'match_file', 'relative_to', 'rglob', 'suffix', "
                        "'supported_extensions']"),
    ("sync-index-renamed", "slopo.indexing.sync.sync_index no longer calls scan_directory by name"),
])
def test_a_moved_or_changed_scanner_runs_slopo_unchanged_and_says_so(tmp_path, patch, detail):
    root = seam_tree(tmp_path)
    res, p = drive({"op": "launch", "argv": ["--config", str(conf(tmp_path, ["/*", "/*/", "!/src/"])), "index"],
                    "cwd": str(root), "patches": [patch]})
    lines = slopo_run_lines(p.stderr)
    assert res["rc"] == 0 and not res["installed"] and len(lines) == 1, (res, p.stderr)
    assert lines[0].startswith("slopo_run: seam check 'scanner' failed (" + detail), lines
    assert lines[0].endswith("; running slopo unchanged")
    assert "Indexed 1 code units from 1 files" in p.stdout            # slopo ran, with the scan it was given
    if patch == "foreign-scan":
        assert res["foreign_calls"] == 1                              # the foreign function, not the walker


@needs_slopo
def test_a_rule_pathspec_contradicts_falls_back_to_slopo_s_scan(tmp_path):
    root = build(tmp_path / "t", ["keep/k.py", "keep/x.py", "other/o.py"])
    c = conf(tmp_path, ["/*", "/*/", "!/keep/"])
    res, p = drive({"op": "launch", "argv": ["--config", str(c), "index"], "cwd": str(root),
                    "patches": ["wrong-prefix"]})        # the rule now claims "!/keep/" matches nothing below keep/
    assert res["rc"] == 0 and res["installed"]
    assert slopo_run_lines(p.stderr) == ["slopo_run: pathspec keeps keep/x.cs, which the pruning rule would skip; "
                                         "this walk is slopo's own scan"]
    assert "Indexed 2 code units from 2 files" in p.stdout            # keep/k.py and keep/x.py: slopo's own result


# ---------- 6. end to end: the databases slopo and the launcher write ----------

def db_rows(path):
    con = sqlite3.connect(str(path))
    try:
        return (con.execute("SELECT id, path, mtime FROM files ORDER BY id").fetchall(),
                con.execute("SELECT id, file_id, name, start_line, end_line, body_hash FROM code_units ORDER BY id")
                .fetchall())
    finally:
        con.close()


@needs_slopo
def test_launcher_and_slopo_write_the_same_index(tmp_path):
    root = build(tmp_path / "t", CASES["pc-shape"][1] + ["scripts/b/c.py", "src/z/y.py", "harness-ports/q/r.py"])
    env = {**os.environ, "LITELLM_LOCAL_MODEL_COST_MAP": "True"}
    a = subprocess.run([str(SLOPO_PY), str(SLOPO_BIN), "--config", str(conf(tmp_path, name="a")), "index"], cwd=root,
                       env=env, capture_output=True, text=True, timeout=300)
    b = subprocess.run([str(SLOPO_PY), str(LAUNCHER), "--config", str(conf(tmp_path, name="b")), "index"], cwd=root,
                       env=env, capture_output=True, text=True, timeout=300)
    assert a.returncode == b.returncode == 0 and a.stdout == b.stdout and b.stderr == "", b.stderr
    files_a, units_a = db_rows(tmp_path / "a.db")
    assert len(files_a) == 8 and db_rows(tmp_path / "b.db") == (files_a, units_a)
    # the control: a walker in the other interpreter's order writes the same files under other ids
    res, _ = drive({"op": "launch", "argv": ["--config", str(conf(tmp_path, name="c")), "index"], "cwd": str(root),
                    "patches": ["flip-lifo"]})
    files_c, _ = db_rows(tmp_path / "c.db")
    assert res["installed"] and sorted(p for _, p, _ in files_c) == sorted(p for _, p, _ in files_a)
    assert files_c != files_a


@needs_slopo
def test_launcher_exits_with_slopo_s_code(tmp_path):
    raw = yaml.safe_load(conf(tmp_path).read_text())
    raw["source_dir"] = str(tmp_path / "missing")
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(raw))
    env = {**os.environ, "LITELLM_LOCAL_MODEL_COST_MAP": "True"}
    a = subprocess.run([str(SLOPO_PY), str(SLOPO_BIN), "--config", str(bad), "index"], cwd=tmp_path, env=env,
                       capture_output=True, text=True, timeout=300)
    b = subprocess.run([str(SLOPO_PY), str(LAUNCHER), "--config", str(bad), "index"], cwd=tmp_path, env=env,
                       capture_output=True, text=True, timeout=300)
    assert a.returncode == b.returncode == 1 and a.stderr == b.stderr and "is not a directory" in b.stderr
    c = subprocess.run([str(SLOPO_PY), str(lock_root(tmp_path, "0.0.0") / LAUNCHER.name), "--config", str(bad),
                        "index"], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=300)
    assert c.returncode == 1 and c.stderr.endswith(a.stderr) and "seam check 'version' failed" in c.stderr


# ---------- 7. --compare ----------

def compare_tree(tmp_path):
    return build(tmp_path / "t", CASES["pc-shape"][1] + ["scripts/b/c.py", "src/z/y.py"])


@needs_slopo
def test_compare_exits_0_on_equal_lists(tmp_path):
    root = compare_tree(tmp_path)
    p = subprocess.run([str(SLOPO_PY), str(LAUNCHER), "--compare", "--config", str(conf(tmp_path))], cwd=root,
                       capture_output=True, text=True, timeout=300)
    lines = p.stdout.splitlines()
    assert p.returncode == 0, p.stdout + p.stderr
    assert lines[:4] == ["slopo_run compare: count slopo 7 walker 7", "slopo_run compare: only in slopo 0 []",
                         "slopo_run compare: only in walker 0 []", "slopo_run compare: order same"]
    assert lines[4].startswith("slopo_run compare: wall slopo ") and len(lines) == 6
    assert lines[5].startswith("slopo_run compare: walker read 12 directories, pruned 9 ") and "'.lanes'" in lines[5]


@needs_slopo
@pytest.mark.parametrize("patch,want", [
    ("too-many:scripts/b", "slopo_run compare: only in slopo 1 ['scripts/b/c.py']"),
    ("flip-lifo", "slopo_run compare: order differs (first at index "),
    ("wrong-prefix", "slopo_run compare: pathspec keeps "),
])
def test_compare_exits_1_when_the_walker_is_wrong(tmp_path, patch, want):
    root = compare_tree(tmp_path)
    res, p = drive({"op": "compare", "argv": ["--config", str(conf(tmp_path))], "cwd": str(root), "patches": [patch]})
    assert res["rc"] == 1 and any(ln.startswith(want) for ln in p.stdout.splitlines()), p.stdout


@needs_slopo
def test_compare_exits_2_on_usage_and_3_on_a_failed_seam_check(tmp_path):
    root = compare_tree(tmp_path)
    u = subprocess.run([str(SLOPO_PY), str(LAUNCHER), "--compare", "--bogus"], cwd=root, capture_output=True,
                       text=True, timeout=300)
    assert u.returncode == 2 and u.stderr.strip() == "usage: slopo_run.py --compare [--config PATH]"
    m = subprocess.run([str(SLOPO_PY), str(LAUNCHER), "--compare", "--config", "none.yaml"], cwd=root,
                       capture_output=True, text=True, timeout=300)
    assert m.returncode == 2 and m.stderr.startswith("slopo_run compare: no config file found at none.yaml")
    s = subprocess.run([str(SLOPO_PY), str(lock_root(tmp_path, "9.9.9") / LAUNCHER.name), "--compare", "--config",
                        str(conf(tmp_path))], cwd=root, capture_output=True, text=True, timeout=300)
    assert s.returncode == 3 and s.stdout.strip() == ("slopo_run compare: seam check 'version' failed (installed "
                                                      "slopo 0.6.0, upstream.lock.yaml pins 9.9.9)")
