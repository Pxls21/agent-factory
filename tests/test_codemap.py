"""L2a (D-090, design L2): scripts/codemap.py, the code-map cache, and the post-commit refresh that feeds it.

Every pack here is built by the REAL instruments (graft, GitNexus, code-review-graph and scripts/ap_screen.py) on a
throwaway repository: one fixture repo is indexed once per module under an isolated HOME (GitNexus keeps its registry
there), and each test works on a copy of it (GitNexus registers the copy with `gitnexus index`; code-review-graph stores
absolute paths, so the copy's graph is rebuilt). The shared indexes of this tree are never touched. The oracles are
independent of the code under test: symbol spans from Python's own `ast`, blob ids from `git hash-object`, risk from
GitNexus's per-symbol CLI, registry rows by the fixture's design, file sizes by `wc`.

The post-commit tests run the real hook (scripts/hooks/post-commit, copied in) through `git commit` with the re-index
slowed by shims that sleep inside the hook's own lock before running the real tool, and record when each re-index
started and ended; the refresh must build after the last end. Each check is a function run on the real code and on
mutated copies of it (one mutation per property, each applied exactly once): a mutant must fail the same check.

Needs graft, gitnexus and code-review-graph installed (scripts/setup.sh); without them those tests skip, and say why.
Deterministic and LLM-free.
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CODEMAP = ROOT / "scripts" / "codemap.py"
HOOK = ROOT / "scripts" / "hooks" / "post-commit"
CRG_FALLBACK = "/root/venv-crg/bin/code-review-graph"
TOOLS = {"graft": shutil.which("graft"), "gitnexus": shutil.which("gitnexus"), "node": shutil.which("node"),
         "code-review-graph": shutil.which("code-review-graph")
         or (CRG_FALLBACK if os.access(CRG_FALLBACK, os.X_OK) else None)}
MISSING = sorted(k for k, v in TOOLS.items() if not v)
needs_tools = pytest.mark.skipif(bool(MISSING), reason="not installed: %s (scripts/setup.sh installs them)"
                                 % ", ".join(MISSING))
SLOW = 2.0                          # seconds each shimmed re-index sleeps inside its lock before it runs
WAIT = 150.0                        # the bound on every wait for a background result

ALPHA = '''"""alpha: the code-map fixture (L2a)."""
import functools
import hashlib
import os

MODE = os.environ.get("ALPHA_MODE", "")


def helper(x):
    try:
        return x + 1
    except TypeError:
        return 0


class Box:
    def __init__(self, v):
        self.v = helper(v)

    def get(self):
        return self.v


@functools.lru_cache(maxsize=None)
def cached(n):
    return hashlib.sha256(str(n).encode()).hexdigest()


def main():
    def inner(y):
        return Box(y).get()
    try:
        return inner(1) + len(cached(2))
    except TypeError:
        return 0
'''
BETA = '''from alpha import helper, Box


def use():
    return helper(2) + Box(3).get()
'''
USER = '''from alpha import cached


def fetch():
    return cached(7)
'''
TEST_ALPHA = '''import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from alpha import helper  # noqa: E402


def test_helper_adds_one():
    assert helper(1) == 2
'''
TOOL_SH = '''#!/bin/bash
greet() {
  echo "hi $1"
}
greet world
'''
WIDE = "字" * 40                # 3 bytes each in UTF-8: the entry passes the byte cap
LONG = ('''"""long: an entry longer than the byte cap."""
import os


def a_function_whose_name_is_long_enough_to_fill_the_head_line_of_its_entry(first_argument, second_argument):
    a = os.environ.get("%s_1")
    b = os.environ.get("%s_2")
    c = os.environ.get("%s_3")
    d = os.environ.get("%s_4")
    return a, b, c, d, first_argument, second_argument
''' % (WIDE, WIDE, WIDE, WIDE))
FILES = {"scripts/alpha.py": ALPHA, "scripts/beta.py": BETA, "scripts/user.py": USER, "tests/test_alpha.py": TEST_ALPHA,
         "scripts/tool.sh": TOOL_SH, "scripts/long.py": LONG, "README.md": "# fixture\n"}
# the tools the hook and the refresh run, never committed in the fixture (a commit must not carry them)
TOOLING = {"scripts/codemap.py": CODEMAP, "scripts/ap_screen.py": ROOT / "scripts" / "ap_screen.py",
           ".claude/hooks/edit-snapshot.py": ROOT / ".claude" / "hooks" / "edit-snapshot.py",
           "scripts/hooks/post-commit": HOOK}
EXCLUDE = "\n".join(list(TOOLING) + [".gitnexus/", "graft/", ".code-review-graph/", ".claude/skills/", ".jev/",
                                     ".gitignore", ".ignore", "AGENTS.md", "CLAUDE.md"]) + "\n"


# ---------- the fixture: one indexed repo per module, a copy per test ----------

def _run(argv, cwd, env, timeout=180, check=True):
    r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    if check:
        assert r.returncode == 0, (argv, r.returncode, r.stdout[-800:], r.stderr[-800:])
    return r


def _env(home, path_dirs=None, **extra):
    dirs = path_dirs if path_dirs is not None else [os.path.dirname(TOOLS[k]) for k in ("graft", "gitnexus", "node")]
    seen = []
    for d in list(dirs) + ["/usr/bin", "/bin"]:
        if d and d not in seen:
            seen.append(d)
    return {"PATH": ":".join(seen), "HOME": str(home), "DO_NOT_TRACK": "1", "LANG": "C.UTF-8", **extra}


def _git(repo, env, *args):
    return _run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.hooksPath=/dev/null", *args], repo,
                env).stdout


def _index(repo, env, graphs=("graft", "gitnexus", "code-review-graph")):
    if "graft" in graphs:
        _run([TOOLS["graft"], "build"], repo, env)
    if "gitnexus" in graphs:
        _run([TOOLS["gitnexus"], "analyze", "--skip-agents-md"], repo, env, timeout=300)
    if "code-review-graph" in graphs:
        _run([TOOLS["code-review-graph"], "build"], repo, env)


@pytest.fixture(scope="module")
def base(tmp_path_factory):
    if MISSING:
        pytest.skip("not installed: %s" % ", ".join(MISSING))
    d = tmp_path_factory.mktemp("codemap")
    home, repo = d / "home", d / "base"
    home.mkdir()
    repo.mkdir()
    env = _env(home)
    _git(repo, env, "init", "-q")
    (repo / ".git" / "info" / "exclude").write_text(EXCLUDE)
    for rel, text in FILES.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")
    for rel, src in TOOLING.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, repo / rel)
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "fixture")
    assert _git(repo, env, "ls-files").split() == sorted(FILES)       # the tooling is never part of a commit
    _index(repo, env)
    return {"home": home, "repo": repo}


@pytest.fixture(autouse=True)
def _drop_the_copy(tmp_path):
    """Each copy holds about 7 MB (GitNexus's DB): removed after its test, so a run keeps one copy at a time."""
    yield
    shutil.rmtree(tmp_path / "repo", ignore_errors=True)


def clone(base, tmp_path, codemap=None, hook=None):
    """A copy of the indexed fixture, with `codemap` / `hook` text in place of the real files when given (a mutant)."""
    repo = tmp_path / "repo"
    shutil.copytree(base["repo"], repo, symlinks=True)
    if codemap is not None:
        (repo / "scripts" / "codemap.py").write_text(codemap, encoding="utf-8")
    if hook is not None:
        (repo / "scripts" / "hooks" / "post-commit").write_text(hook, encoding="utf-8")
    env = _env(base["home"])
    _run([TOOLS["gitnexus"], "index", str(repo)], repo, env)
    _index(repo, env, graphs=("code-review-graph",))
    return repo


def mutate(src_path, old, new):
    text = Path(src_path).read_text(encoding="utf-8")
    assert text.count(old) == 1, "the mutation anchor must occur exactly once: %r" % old[:80]
    return text.replace(old, new)


def load(repo):
    """The copy's codemap.py as a module (lookups read packs and files only, so they run in process)."""
    spec = importlib.util.spec_from_file_location("codemap_%d" % time.monotonic_ns(), repo / "scripts" / "codemap.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(repo, base, *rels, path_dirs=None):
    r = _run([sys.executable, "scripts/codemap.py", "build", *rels], repo, _env(base["home"], path_dirs))
    return r.stdout


def pack(repo, rel):
    return json.loads((repo / ".jev" / "codemap" / (rel + ".json")).read_text(encoding="utf-8"))


def ast_symbols(text):
    """(qualname, def line, end line, first decorator line): the oracle for the pack's spans."""
    import ast
    out = []

    def walk(node, prefix):
        for n in ast.iter_child_nodes(node):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = prefix + n.name
                out.append((q, n.lineno, n.end_lineno, min([d.lineno for d in n.decorator_list] or [n.lineno])))
                walk(n, q + ".")
            else:
                walk(n, prefix)
    walk(ast.parse(text), "")
    return sorted(out, key=lambda s: (s[1], s[0]))


# ---------- the checks (each also runs on a mutant, which must fail it) ----------

def check_pack_fields(repo, base):
    build(repo, base, "scripts/alpha.py")
    p = pack(repo, "scripts/alpha.py")
    data = (repo / "scripts" / "alpha.py").read_bytes()
    assert p["schema"] == 1 and p["path"] == "scripts/alpha.py" and p["language"] == "python"
    assert p["blob"] == _run(["git", "hash-object", "scripts/alpha.py"], repo, _env(base["home"])).stdout.strip(), \
        "blob is not git's blob id"
    assert p["sha256"] == hashlib.sha256(data).hexdigest() and p["bytes"] == len(data)
    assert p["lines"] == int(_run(["wc", "-l", "scripts/alpha.py"], repo, _env(base["home"])).stdout.split()[0])
    assert p["commit"] == _git(repo, _env(base["home"]), "rev-parse", "HEAD").strip()
    ins = p["instruments"]
    assert {k: (ins[k]["status"], ins[k].get("graph")) for k in ins} == {
        "graft": ("ok", "fresh"), "gitnexus": ("ok", "fresh"), "code-review-graph": ("ok", "fresh"),
        "ap_screen": ("ok", None)}, "an instrument section is not ok and fresh"
    got = [(s["qualname"], s["start"], s["end"], s.get("from", s["start"])) for s in p["symbols"]]
    assert got == ast_symbols(data.decode()), "the symbols and spans differ from the file's own AST"
    by = {s["qualname"]: s for s in p["symbols"]}
    helper = by["helper"]["gitnexus"]
    assert helper["risk"] == "LOW" and helper["callers"]["count"] == 3 and helper["callers"]["tests"] == 1
    assert [(c["name"], c["file"], c["line"]) for c in helper["callers"]["sample"]] == [
        ("use", "scripts/beta.py", 4), ("__init__", "scripts/alpha.py", 17), ("test_helper_adds_one",
                                                                              "tests/test_alpha.py", 8)]
    assert by["main"]["gitnexus"]["risk"] == "UNKNOWN" and by["main"]["gitnexus"]["callers"]["count"] == 0
    assert [(t["file"], t["name"]) for t in p["tests"]] == [("tests/test_alpha.py", "test_helper_adds_one")]
    assert [(h["row"], h["line"]) for h in p["registry"]] == [("AP-1", 6), ("AP-32", 26)]
    assert all(h["message"] for h in p["registry"])
    assert p["caller_files"] == ["scripts/beta.py", "scripts/user.py", "tests/test_alpha.py"]


def check_lookup_positions(repo, base):
    build(repo, base, "scripts/alpha.py")
    cm = load(repo)

    def at(line, end=None):
        return cm.lookup("scripts/alpha.py", line, end, root=repo)
    r = at(11)
    assert (r["status"], r["symbol"]["qualname"], r["stale"]) == ("hit", "helper", False), r
    assert "risk LOW" in r["text"] and "use scripts/beta.py:4" in r["text"]
    r = at(21)
    assert (r["status"], r["symbol"]["qualname"]) == ("hit", "Box.get"), "a method line did not give the method"
    r = at(31)
    assert (r["status"], r["symbol"]["qualname"]) == ("hit", "main.inner"), "a nested line did not give the inner def"
    r = at(24)
    assert (r["status"], r["symbol"]["qualname"]) == ("hit", "cached"), "a decorator line did not give its def"
    r = at(22)
    assert (r["status"], r["symbol"]) == ("module", None), "a blank line between two defs"
    r = at(6)
    assert (r["status"], r["symbol"]) == ("module", None), "a module-level line"
    assert "module level" in r["text"] and "AP-1 :6" in r["text"]
    r = at(999)
    assert r["status"] == "past-end" and "past the end" in r["text"], "a line past the end: %s" % r["status"]
    r = at(33)
    assert r["symbol"]["qualname"] == "main" and "risk UNKNOWN" in r["text"]
    assert "unresolved, not zero" in r["text"], "UNKNOWN is not said as unresolved"
    r = at(18, 21)
    assert (r["status"], r["symbol"]["qualname"]) == ("hit", "Box"), "a range over two methods is their class"


def check_stale(repo, base):
    build(repo, base, "scripts/alpha.py")
    cm = load(repo)
    assert cm.lookup("scripts/alpha.py", 11, root=repo)["stale"] is False
    f = repo / "scripts" / "alpha.py"
    f.write_text(f.read_text() + "\n# edited\n")
    r = cm.lookup("scripts/alpha.py", 11, root=repo)
    assert r["stale"] is True and "STALE" in r["text"], "an edited file was not flagged stale"


def check_miss(repo, base):
    cm = load(repo)
    r = cm.lookup("scripts/beta.py", 4, root=repo)                  # no pack was built for beta.py
    assert r["status"] == "miss" and r["stale"] is None and "no pack" in r["text"], "a missing pack is not a miss"
    r = cm.lookup("README.md", 1, root=repo)
    assert r["status"] == "out-of-scope", r


def check_byte_cap(repo, base):
    build(repo, base, "scripts/long.py")
    cm = load(repo)
    r = cm.lookup("scripts/long.py", 6, root=repo)
    raw = r["text"].encode("utf-8")
    assert r["status"] == "hit" and len(raw) <= 1500, "the entry is %d bytes" % len(raw)
    assert r["text"].endswith("…[cut at 1500 bytes]") and raw.decode("utf-8")
    for line in range(1, 12):                                        # every entry of both files stays under the cap
        assert len(cm.lookup("scripts/long.py", line, root=repo)["text"].encode()) <= 1500


def check_absent(repo, base):
    crg_dir = os.path.dirname(TOOLS["code-review-graph"])
    out = build(repo, base, "scripts/alpha.py", path_dirs=[crg_dir] if crg_dir != os.path.dirname(CRG_FALLBACK) else [])
    p = pack(repo, "scripts/alpha.py")
    assert p["instruments"]["graft"]["status"] == "absent" and "not installed" in p["instruments"]["graft"]["note"], \
        "an absent graft is not named absent"
    assert p["instruments"]["gitnexus"]["status"] == "absent"
    assert p["symbols_from"] == "code-review-graph" and all(s["gitnexus"] is None for s in p["symbols"]), out
    text = load(repo).lookup("scripts/alpha.py", 11, root=repo)["text"]
    assert "GitNexus absent" in text and "graft absent" in text


def check_identical(repo, base):
    build(repo, base, "scripts/alpha.py", "scripts/tool.sh")
    first = {r: pack(repo, r) for r in ("scripts/alpha.py", "scripts/tool.sh")}
    build(repo, base, "scripts/alpha.py", "scripts/tool.sh")
    for rel, p in first.items():
        q = pack(repo, rel)
        for d in (p, q):
            d.pop("timing")
            d.pop("built_at")
        assert p == q, "two builds of %s on one index differ apart from times" % rel


def check_edit_context(repo, base):
    build(repo, base, "scripts/alpha.py")
    cm = load(repo)
    old = "    try:\n        return inner(1)"          # its first line occurs first inside helper (D8)
    r = cm.edit_context(str(repo / "scripts" / "alpha.py"), old, root=repo)
    assert (r["status"], r["ranges"]) == ("hit", [(32, 33)]), "the edit was not placed at 32-33: %s" % r["text"]
    assert r["symbol"]["qualname"] == "main"
    r = cm.edit_context("scripts/alpha.py", "    except TypeError:\n        return 0", root=repo)
    assert r["status"] == "ambiguous" and r["ranges"] == [(12, 13), (34, 35)], r
    r = cm.edit_context("scripts/alpha.py", "not in the file", root=repo)
    assert r["status"] == "miss"
    payload = repo / "payload.json"
    payload.write_text(json.dumps({"tool_name": "Edit", "tool_input": {
        "file_path": str(repo / "scripts" / "alpha.py"), "old_string": old, "new_string": old + "  # x"}}))
    out = _run([sys.executable, "scripts/codemap.py", "demo", str(payload)], repo, _env(base["home"])).stdout
    assert out.startswith("old_string at: L32-33\nenclosing: main\n") and "risk UNKNOWN" in out


def check_record_that_lies(repo, base):
    """GitNexus's own record claims the file's current bytes while its nodes are older (measured on this tree:
    proofs/S0-08/check_containment.py kept its 09-14 spans under the current sha256). Reproduced here: alpha.py gains
    three lines, graft and code-review-graph re-index, GitNexus does not, and its fileHashes entry is set to the new
    sha256. The pack must not call that graph fresh, and still joins its data by name, flagged."""
    env = _env(base["home"])
    f = repo / "scripts" / "alpha.py"
    f.write_text("# one\n# two\n# three\n" + ALPHA)
    _index(repo, env, graphs=("graft", "code-review-graph"))
    meta = json.loads((repo / ".gitnexus" / "meta.json").read_text())
    meta["fileHashes"]["scripts/alpha.py"] = hashlib.sha256(f.read_bytes()).hexdigest()
    (repo / ".gitnexus" / "meta.json").write_text(json.dumps(meta))
    build(repo, base, "scripts/alpha.py")
    p = pack(repo, "scripts/alpha.py")
    g = p["instruments"]["gitnexus"]
    assert g["graph"] == "stale" and "its record claims these bytes" in g.get("note", ""), \
        "a graph whose nodes predate its record is not marked stale"
    helper = {s["qualname"]: s for s in p["symbols"]}["helper"]
    assert helper["start"] == 12 and helper["gitnexus"]["matched_by"].startswith("name")
    assert helper["gitnexus"]["risk"] == "LOW"
    assert "from a STALE GitNexus graph" in load(repo).lookup("scripts/alpha.py", 14, root=repo)["text"]


LOOKUP_CHECKS = {"pack-fields": check_pack_fields, "record-that-lies": check_record_that_lies, "lookup-positions": check_lookup_positions, "stale": check_stale,
                 "miss": check_miss, "byte-cap": check_byte_cap, "absent": check_absent,
                 "identical": check_identical, "edit-context": check_edit_context}
# one mutation per property: (the check it must fail, old text, new text, the failure it must fail with)
MUTANTS = {
    "blob-without-header": ("pack-fields", 'hashlib.sha1(b"blob %d\\0" % len(data) + data)', "hashlib.sha1(data)",
                            "blob is not git's blob id"),
    "spans-without-decorators": ("pack-fields", '            s["from"] = first[(s["name"], s["start"])]',
                                 "            pass", "the symbols and spans differ from the file's own AST"),
    "outermost-symbol": ("lookup-positions", 'sym = max(enclosing, key=lambda s: (s["start"], -s["end"]))',
                         'sym = min(enclosing, key=lambda s: (s["start"], -s["end"]))',
                         "a method line did not give the method"),
    "no-past-end": ("lookup-positions", 'if line > pack["lines"]:', 'if line > pack["lines"] + 10 ** 6:',
                    "a line past the end: module"),
    "unknown-read-as-none": ("lookup-positions", 'line = "risk UNKNOWN — " + UNRESOLVED % s["name"]',
                             'line = "risk UNKNOWN — no callers"', "UNKNOWN is not said as unresolved"),
    "never-stale": ("stale", 'stale = blob_sha((root / rel).read_bytes()) != pack["blob"]', "stale = False",
                    "an edited file was not flagged stale"),
    "miss-as-module": ("miss", 'return dict(res, status="miss", text="codemap: %s for %s',
                       'return dict(res, status="module", text="codemap: %s for %s', "a missing pack is not a miss"),
    "no-cap": ("byte-cap", "TEXT_CAP = 1500 ", "TEXT_CAP = 10 ** 9 ", r"the entry is 1[5-9]\d\d bytes"),
    "absent-as-empty": ("absent", 'return {"status": "absent", "note": "graft is not installed (not on PATH)"}, []',
                        'return {"status": "no-data", "note": ""}, []', "an absent graft is not named absent"),
    "time-in-a-field": ("identical", '"commit": commit, "symbols_from"', '"commit": "%s %f" % (commit, time.time()), '
                        '"symbols_from"', "two builds of scripts/alpha.py on one index differ apart from times"),
    "trust-the-record": ("record-that-lies", '    if moved and sec.get("graph") == "fresh":', "    if False:",
                         "a graph whose nodes predate its record is not marked stale"),
    "first-line-only": ("edit-context", "ranges, i = [], content.find(old_string)",
                        'ranges, i = [], content.find(old_string.split("\\n", 1)[0])',
                        "the edit was not placed at 32-33: codemap: old_string occurs 2 times"),
}


@needs_tools
@pytest.mark.parametrize("name", sorted(LOOKUP_CHECKS))
def test_check_passes_on_the_real_codemap(base, tmp_path, name):
    LOOKUP_CHECKS[name](clone(base, tmp_path), base)


@needs_tools
@pytest.mark.parametrize("mutant", sorted(MUTANTS))
def test_negative_control_the_same_check_fails_on_a_mutant(base, tmp_path, mutant):
    check, old, new, why = MUTANTS[mutant]
    repo = clone(base, tmp_path, codemap=mutate(CODEMAP, old, new))
    with pytest.raises(AssertionError, match=why):
        LOOKUP_CHECKS[check](repo, base)


@needs_tools
def test_every_mutant_is_graded_by_a_check():
    assert set(LOOKUP_CHECKS) == {m[0] for m in MUTANTS.values()}, "a property has no mutant, or a mutant no check"


@needs_tools
def test_risk_equals_gitnexus_per_symbol_cli(base, tmp_path):
    """The batched session gives the same risk as one CLI call per symbol (the form the brief measured)."""
    repo = clone(base, tmp_path)
    build(repo, base, "scripts/alpha.py")
    env = _env(base["home"])
    seen = 0
    for s in pack(repo, "scripts/alpha.py")["symbols"]:
        if s["qualname"] not in ("helper", "main", "Box.get"):
            continue
        cli = json.JSONDecoder().raw_decode(_run([TOOLS["gitnexus"], "impact", "--uid", s["gitnexus"]["id"],
                                                  "--summary-only", "--repo", str(repo)], repo, env).stdout)[0]
        assert (cli["risk"], cli["impactedCount"]) == (s["gitnexus"]["risk"], s["gitnexus"]["impacted"]), s
        seen += 1
    assert seen == 3


@needs_tools
def test_shell_file_gets_crg_symbols_and_says_what_is_not_parsed(base, tmp_path):
    repo = clone(base, tmp_path)
    build(repo, base, "scripts/tool.sh")
    p = pack(repo, "scripts/tool.sh")
    assert p["language"] == "shell" and p["symbols_from"] == "code-review-graph"
    assert [(s["qualname"], s["start"], s["end"]) for s in p["symbols"]] == [("greet", 2, 4)]
    assert (p["instruments"]["graft"]["status"], p["instruments"]["gitnexus"]["status"]) == ("n/a", "n/a")
    text = load(repo).lookup("scripts/tool.sh", 3, root=repo)["text"]
    assert "GitNexus n/a (GitNexus does not parse this file type)" in text


# ---------- the post-commit refresh: ordering, docs-only, widening ----------

SHIM = '''#!/bin/sh
case "$1" in build|analyze|update)
  printf '%%s start %%s\\n' "%(name)s" "$(date +%%s.%%N)" >> "$SLOW_RECORD"; sleep "$SLOW" ;; esac
"%(real)s" "$@"; rc=$?
case "$1" in build|analyze|update) printf '%%s end %%s\\n' "%(name)s" "$(date +%%s.%%N)" >> "$SLOW_RECORD" ;; esac
exit $rc
'''


def shims(tmp_path):
    d = tmp_path / "shims"
    d.mkdir()
    for name in ("graft", "gitnexus", "code-review-graph"):
        (d / name).write_text(SHIM % {"name": name, "real": TOOLS[name]})
        (d / name).chmod(0o755)
    (d / "codebase-memory-mcp").write_text("#!/bin/sh\nexit 0\n")          # the fourth graph is not read here
    (d / "codebase-memory-mcp").chmod(0o755)
    return d


def records(path, want, timeout=WAIT):
    deadline = time.monotonic() + timeout
    while True:
        got = path.read_text().splitlines() if path.exists() else []
        if len([g for g in got if " end " in g]) >= want or time.monotonic() > deadline:
            return got
        time.sleep(0.2)


def log_line(path, pattern, timeout=WAIT):
    deadline = time.monotonic() + timeout
    while True:
        lines = path.read_text().splitlines() if path.exists() else []
        hit = [ln for ln in lines if re.search(pattern, ln)]
        if hit or time.monotonic() > deadline:
            return hit[-1] if hit else None
        time.sleep(0.2)


def add_gamma(repo):
    (repo / "scripts" / "alpha.py").write_text(ALPHA + "\n\ndef gamma(y):\n    return helper(y) * 2\n")
    (repo / "scripts" / "beta.py").write_text(BETA.replace("helper, Box", "helper, Box, gamma").replace(
        "Box(3).get()", "Box(3).get() + gamma(4)"))


def check_commit_refresh_after_reindex(repo, base, tmp_path):
    """A code commit through the real hook: the refresh builds after the slowed re-index of every graph it reads."""
    t, rec = tmp_path / "t", tmp_path / "slow.txt"
    t.mkdir()
    env = _env(base["home"], [str(shims(tmp_path)), os.path.dirname(TOOLS["node"])], AF_POST_COMMIT_TMP=str(t),
               SLOW=str(SLOW), SLOW_RECORD=str(rec))
    add_gamma(repo)
    _git(repo, env, "add", "-A")
    _run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.hooksPath=scripts/hooks", "commit", "-q",
          "-m", "gamma"], repo, env)
    launch = (t / "codemap-refresh.log").read_text().splitlines()     # read the moment the commit returned
    assert not any(" done: " in ln for ln in launch), "the commit waited on the refresh"
    assert len(launch) == 1 and re.search(r" codemap refresh launched: 2 path\(s\) \(first: scripts/alpha\.py\), "
                                          r"after the re-index of: graft gitnexus codebase-memory code-review-graph$",
                                          launch[0]), launch
    done = log_line(t / "codemap-refresh.log", r" codemap refresh done: ")
    ends = records(rec, 3)                                           # never leave a re-index running past the test
    assert done and " 2 built" in done, done
    end = max(float(r.split()[2]) for r in ends if " end " in r)
    p = pack(repo, "scripts/alpha.py")
    assert p["timing"]["started"] > end, "the pack was built before the re-index ended"
    assert {k: p["instruments"][k]["graph"] for k in ("graft", "gitnexus", "code-review-graph")} == dict.fromkeys(
        ("graft", "gitnexus", "code-review-graph"), "fresh")
    g = {s["qualname"]: s for s in p["symbols"]}["gamma"]["gitnexus"]
    assert [(c["name"], c["file"]) for c in g["callers"]["sample"]] == [("use", "scripts/beta.py")]


def check_refresh_that_starts_first_waits(repo, base, tmp_path):
    """The race the brief names: the refresh starts BEFORE the re-index has taken its lock; it must still build from
    the re-indexed graphs (the lock is free at its first look, so only the per-file stamps can hold it back)."""
    t, rec = tmp_path / "t", tmp_path / "slow.txt"
    t.mkdir()
    env = _env(base["home"], [str(shims(tmp_path)), os.path.dirname(TOOLS["node"])], SLOW=str(SLOW),
               SLOW_RECORD=str(rec))
    add_gamma(repo)
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "gamma")                  # hooks off: no re-index yet
    head = _git(repo, env, "rev-parse", "HEAD").strip()
    ref = subprocess.Popen([sys.executable, "scripts/codemap.py", "refresh", "--commit", head, "--lock-dir", str(t),
                            "--graphs", "graft gitnexus code-review-graph", "--grace", "30", "--poll", "0.2", "--",
                            "scripts/alpha.py", "scripts/beta.py"], cwd=repo, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
    try:
        time.sleep(1.5)
        # the hook's own launch lines: each re-index under its lock, `flock -n`, in the background
        launch = ('( flock -n 9 || exit 0; graft build >/dev/null 2>&1 ) 9>"$T/graft-build.lock" &\n'
                  '( flock -n 9 || exit 0; gitnexus analyze --skip-agents-md >/dev/null 2>&1 ) '
                  '9>"$T/gitnexus-analyze.lock" &\n'
                  '( flock -n 9 || exit 0; { code-review-graph update >/dev/null 2>&1 || code-review-graph build '
                  '>/dev/null 2>&1; } ) 9>"$T/crg-build.lock" &\n')
        _run(["bash", "-c", launch], repo, dict(env, T=str(t)))
        out, _ = ref.communicate(timeout=WAIT)
    finally:
        if ref.poll() is None:
            ref.kill()
            ref.wait()
        ends = records(rec, 3)
    end = max(float(r.split()[2]) for r in ends if " end " in r)
    p = pack(repo, "scripts/alpha.py")
    assert ref.returncode == 0 and "codemap refresh done: 2 built" in out, out
    assert p["timing"]["started"] > end, "the refresh read the graphs before their re-index ended"
    assert "gamma" in {s["qualname"] for s in p["symbols"]} and all(
        p["instruments"][k]["graph"] == "fresh" for k in ("graft", "gitnexus", "code-review-graph")), out


def check_gives_up_and_marks_stale(repo, base, tmp_path):
    """No re-index ever comes (it was skipped): after the grace the refresh builds and marks the graph stale."""
    env = _env(base["home"])
    add_gamma(repo)
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "gamma")
    t0 = time.monotonic()
    out = _run([sys.executable, "scripts/codemap.py", "refresh", "--commit", "x", "--lock-dir", str(tmp_path),
                "--graphs", "graft", "--grace", "1", "--poll", "0.2", "--", "scripts/alpha.py"], repo, env).stdout
    assert time.monotonic() - t0 < 20
    assert "not ready: graft (it had not indexed scripts/alpha.py)" in out, out
    p = pack(repo, "scripts/alpha.py")
    assert p["instruments"]["graft"]["graph"] == "stale", "a graph that never caught up is not marked stale"
    assert "gamma" not in {s["qualname"] for s in p["symbols"]}
    assert "graft stale" in load(repo).lookup("scripts/alpha.py", 11, root=repo)["text"]


def check_docs_only_commit(repo, base, tmp_path):
    t = tmp_path / "t"
    t.mkdir()
    env = _env(base["home"], [str(shims(tmp_path)), os.path.dirname(TOOLS["node"])], AF_POST_COMMIT_TMP=str(t),
               SLOW="0", SLOW_RECORD=str(tmp_path / "slow.txt"))
    for rel in ("README.md", "scripts/notes.md", "tasks/briefs/probe.py", "wiki/a.md"):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text("x %s\n" % rel)
    _git(repo, env, "add", "-A")
    _run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.hooksPath=scripts/hooks", "commit", "-q",
          "-m", "docs"], repo, env)
    lines = (t / "codemap-refresh.log").read_text().splitlines()
    assert len(lines) == 1 and lines[0].endswith(" codemap refresh none: no changed path under scripts/, src/, "
                                                 "proofs/, spikes/, harness-ports/ (outside the docs plane) or "
                                                 "tests/*.py"), "a docs-only commit launched a refresh: %s" % lines
    time.sleep(2)
    assert not (repo / ".jev").exists() and len((t / "codemap-refresh.log").read_text().splitlines()) == 1


def check_widening(repo, base, tmp_path):
    """A commit that changes only a caller file refreshes the callee's pack too: a call added (GitNexus's edges) and a
    call removed (the old pack named the caller)."""
    env = _env(base["home"])
    build(repo, base, "scripts/alpha.py")
    assert "scripts/user.py" in pack(repo, "scripts/alpha.py")["caller_files"]

    def commit_and_refresh(rel, text):
        (repo / rel).write_text(text)
        _git(repo, env, "add", "-A")
        _git(repo, env, "commit", "-q", "-m", "c")
        _index(repo, env)
        return _run([sys.executable, "scripts/codemap.py", "refresh", "--commit", "x", "--lock-dir", str(tmp_path),
                     "--graphs", "graft gitnexus code-review-graph", "--", rel], repo, env).stdout
    out = commit_and_refresh("scripts/beta.py", BETA.replace("helper, Box", "helper, Box, cached").replace(
        "Box(3).get()", "Box(3).get() + len(cached(1))"))
    assert "widened by 1 whose callers changed: scripts/alpha.py" in out, "an added call did not widen: " + out
    cached = {s["qualname"]: s for s in pack(repo, "scripts/alpha.py")["symbols"]}["cached"]["gitnexus"]["callers"]
    assert ("use", "scripts/beta.py") in [(c["name"], c["file"]) for c in cached["sample"]]
    out = commit_and_refresh("scripts/user.py", "def fetch():\n    return 7\n")       # no call into alpha.py is left
    assert "widened by 1 whose callers changed: scripts/alpha.py" in out, out
    assert "scripts/user.py" not in pack(repo, "scripts/alpha.py")["caller_files"]


REFRESH_CHECKS = {"commit-refresh-after-reindex": check_commit_refresh_after_reindex,
                  "refresh-that-starts-first-waits": check_refresh_that_starts_first_waits,
                  "gives-up-and-marks-stale": check_gives_up_and_marks_stale,
                  "docs-only-commit": check_docs_only_commit, "widening": check_widening}
# (the check, "codemap" or "hook", old text, new text, the failure it must fail with)
REFRESH_MUTANTS = {
    "refresh-without-graphs": ("commit-refresh-after-reindex", "hook", '--graphs "$launched"', '--graphs ""',
                               "the pack was built before the re-index ended"),
    "no-wait": ("refresh-that-starts-first-waits", "codemap", "        if not open_ or now - start >= wait:",
                "        if True:", "the refresh read the graphs before their re-index ended"),
    "lock-only-wait": ("refresh-that-starts-first-waits", "codemap",
                       "behind = [r for r in files if stamp(g, root, r) != _sha256_file(root / r)]", "behind = []",
                       "the refresh read the graphs before their re-index ended"),
    "stale-read-as-fresh": ("gives-up-and-marks-stale", "codemap",
                            'return "not-indexed" if indexed is None else ("fresh" if indexed == sha else "stale")',
                            'return "fresh"', "a graph that never caught up is not marked stale"),
    "docs-plane-not-skipped": ("docs-only-commit", "hook", 'docs_plane "$p" || cm_paths+=("$p")', 'cm_paths+=("$p")',
                               r"a docs-only commit launched a refresh: \['\S+ \w+ codemap refresh launched: 1 path"),
    "no-widening": ("widening", "codemap", "        extra, wnote = widen(root, [r for r in rels if language(root, r)], "
                    "gn)", "        extra, wnote = [], ''", "an added call did not widen"),
}


@needs_tools
@pytest.mark.parametrize("name", sorted(REFRESH_CHECKS))
def test_refresh_check_passes_on_the_real_code(base, tmp_path, name):
    REFRESH_CHECKS[name](clone(base, tmp_path), base, tmp_path)


@needs_tools
@pytest.mark.parametrize("mutant", sorted(REFRESH_MUTANTS))
def test_negative_control_the_refresh_check_fails_on_a_mutant(base, tmp_path, mutant):
    check, which, old, new, why = REFRESH_MUTANTS[mutant]
    kw = {"codemap": mutate(CODEMAP, old, new)} if which == "codemap" else {"hook": mutate(HOOK, old, new)}
    repo = clone(base, tmp_path, **kw)
    with pytest.raises(AssertionError, match=why):
        REFRESH_CHECKS[check](repo, base, tmp_path)


@needs_tools
def test_every_refresh_mutant_is_graded_by_a_check():
    assert set(REFRESH_CHECKS) == {m[0] for m in REFRESH_MUTANTS.values()}


# ---------- static: the hook and codemap agree; the byte cap cuts on a character boundary ----------

def hook_sets(text):
    sets = {}
    for name, value in re.findall(r'^(GRAFT_EXT|GITNEXUS_EXT|CRG_EXT)\+?="([^"]*)"', text, re.M):
        sets.setdefault(name, set()).update(value.split())
    return sets


def hook_locks(text):
    return dict(re.findall(r'^\s+(graft|gitnexus|code-review-graph)\) \( flock -n 9 \|\| exit 0\n(?:.*\n)*?'
                           r'\s+\) 9>"\$T/([\w.-]+)"', text, re.M))


def check_reads_and_locks(cm, text):
    sets = hook_sets(text)
    assert set(sets) == {"GRAFT_EXT", "GITNEXUS_EXT", "CRG_EXT"}, "the hook's read-sets were not all found"
    for graph, var in (("graft", "GRAFT_EXT"), ("gitnexus", "GITNEXUS_EXT"), ("code-review-graph", "CRG_EXT")):
        want = {e for e in cm.LANG if e in sets[var]} | ({""} if graph == "code-review-graph" else set())
        assert cm.READS[graph] == want, (graph, cm.READS[graph] ^ want)
    assert hook_locks(text) == cm.LOCKS, (hook_locks(text), cm.LOCKS)
    assert re.search(r'python3 scripts/codemap\.py refresh --commit "\$cm_head" --lock-dir "\$T"', text)


def test_codemap_reads_and_locks_are_the_hook_s():
    spec = importlib.util.spec_from_file_location("codemap_static", CODEMAP)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    check_reads_and_locks(cm, HOOK.read_text(encoding="utf-8"))


def test_negative_control_a_renamed_lock_or_a_dropped_extension_is_caught():
    spec = importlib.util.spec_from_file_location("codemap_static2", CODEMAP)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    text = HOOK.read_text(encoding="utf-8")
    with pytest.raises(AssertionError, match="crg.lock"):
        check_reads_and_locks(cm, text.replace('9>"$T/crg-build.lock"', '9>"$T/crg.lock"'))
    assert text.count(" mjs mts ") == 1                   # only GITNEXUS_EXT spells it so
    with pytest.raises(AssertionError, match="gitnexus"):
        check_reads_and_locks(cm, text.replace(" mjs mts ", " mts "))


def test_cap_cuts_on_a_character_boundary():
    spec = importlib.util.spec_from_file_location("codemap_cap", CODEMAP)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    for pad in range(4):                               # every offset of a 3-byte character against the cut
        text = "x" * pad + WIDE * 30
        cut = cm._cap(text)
        raw = cut.encode("utf-8")
        assert len(raw) <= 1500 and cut.endswith("…[cut at 1500 bytes]") and raw.decode("utf-8") == cut
        assert 1500 - len(raw) < 3                     # at most one partial character dropped
    assert cm._cap("short") == "short"


HANG = """import json, sys
for line in sys.stdin:                  # answers initialize, then never answers a tool call (a hung server)
    msg = json.loads(line)
    if msg.get("method") == "initialize":
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": {}}) + "\\n")
        sys.stdout.flush()
"""


def test_a_hung_gitnexus_costs_one_timeout_per_build_not_one_per_file(tmp_path):
    """Failure path, through a fake server that hangs (the real one cannot be made to hang on demand): the first
    batch times out, every later call fails at once, and a file's section names the failure (never a silent blank)."""
    spec = importlib.util.spec_from_file_location("codemap_hang", CODEMAP)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    exe = tmp_path / "gitnexus"
    exe.write_text("#!%s\n%s" % (sys.executable, HANG))
    exe.chmod(0o755)
    gn = cm.GitNexus(str(exe), tmp_path, timeout=2.0)
    try:
        t0 = time.monotonic()
        with pytest.raises(TimeoutError):
            gn.tools([("cypher", {"statement": "RETURN 1"})])
        assert 1.5 < time.monotonic() - t0 < 10
        t1 = time.monotonic()
        sec, recs = cm._gitnexus(gn, tmp_path, "scripts/x.py", "0" * 64)
        assert time.monotonic() - t1 < 1.0, "a dead session waited again"
        assert sec["status"] == "error" and "failed earlier in this build" in sec["note"] and recs == []
    finally:
        gn.close()


def test_lock_held_is_read_without_taking_the_lock(tmp_path):
    spec = importlib.util.spec_from_file_location("codemap_lock", CODEMAP)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    lock = tmp_path / "x.lock"
    assert cm.lock_held(lock) is False                            # no such file
    holder = subprocess.Popen(["bash", "-c", 'exec 9>"$0"; flock 9; echo held; sleep 30', str(lock)],
                              stdout=subprocess.PIPE, text=True)
    try:
        assert holder.stdout.readline().strip() == "held"
        assert cm.lock_held(lock) is True
        # a `flock -n` beside it still fails: lock_held took nothing, and the holder still holds
        assert subprocess.run(["flock", "-n", str(lock), "true"]).returncode == 1
    finally:
        holder.kill()
        holder.wait()
    assert cm.lock_held(lock) is False
    assert subprocess.run(["flock", "-n", str(lock), "true"]).returncode == 0
