"""CTX1 (D-089): scripts/hooks/post-commit re-indexes a graph only when the commit changed a file that graph reads.

A commit of only Markdown, wiki/, todo/, transcripts/ or tasks/ launches none of the four graphs (graft, GitNexus,
codebase-memory, code-review-graph); every `gitnexus analyze` the hook runs passes --skip-agents-md, so analyze never
rewrites CLAUDE.md or AGENTS.md; one log line per commit says which graphs were launched or why none was. The owner:
"I don't think anything should be re-indexed unless it's updated first."

The hook runs by hand in a throwaway git repo (its commits are made with hooks off) with FAKE indexers first on PATH:
each fake appends its name and argv to a record file and exits, so no real index is touched. PATH is the fakes plus
/usr/bin:/bin only, so a fake left out can never fall through to the real graft or gitnexus (/opt/node22/bin); the fixed
fallback paths of codebase-memory and code-review-graph are always shadowed by their fakes, which every test installs.
The hook launches in the background: a positive waits (bounded) for its records; a negative reads the hook's own
synchronous log line, then proves no record arrived within the same bounded wait the positives meet. Plus the static
rule over the three scripts: every automatic analyze call site passes --skip-agents-md. Deterministic and LLM-free.
"""
import os
import re
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "hooks" / "post-commit"
FAKES = {"graft": "graft", "gitnexus": "gitnexus", "codebase-memory-mcp": "codebase-memory",
         "code-review-graph": "code-review-graph"}           # fake binary -> the graph name the hook logs
ALL = ["graft", "gitnexus", "codebase-memory", "code-review-graph"]
WAIT = 10.0                                                     # the bounded wait, positives and negatives alike
FAKE_BODY = '#!/bin/sh\nprintf \'%s %s\\n\' "${0##*/}" "$*" >> "$FAKE_RECORD"\n'


class Repo:
    def __init__(self, tmp_path, tools=tuple(FAKES)):
        self.root = tmp_path / "repo"
        self.bin = tmp_path / "bin"
        self.tmp = tmp_path / "t"
        self.record = tmp_path / "record.txt"
        for d in (self.root, self.bin, self.tmp, tmp_path / "home"):
            d.mkdir()
        for name in tools:
            f = self.bin / name
            f.write_text(FAKE_BODY)
            f.chmod(0o755)
        self.env = {"PATH": "%s:/usr/bin:/bin" % self.bin, "HOME": str(tmp_path / "home"), "LC_ALL": "C",
                    "AF_POST_COMMIT_TMP": str(self.tmp), "FAKE_RECORD": str(self.record)}
        self.git("init", "-q")
        self.top = os.path.realpath(str(self.root))

    def git(self, *args):
        r = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "user.email=t@t", "-c", "user.name=t",
                            *args], cwd=self.root, env=self.env, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        return r.stdout

    def commit(self, *paths, msg="c"):
        for rel in paths:
            f = self.root / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("%s %d\n" % (rel, time.monotonic_ns()))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def hook(self):
        r = subprocess.run(["bash", str(HOOK)], cwd=self.root, env=self.env, capture_output=True, text=True,
                           timeout=60)
        assert r.returncode == 0 and r.stderr == "", (r.returncode, r.stderr)
        return (self.log() or [None])[-1]

    def log(self):
        p = self.tmp / "post-commit-reindex.log"
        return p.read_text().splitlines() if p.exists() else []

    def records(self, want=0):
        """The fake records once `want` lines have arrived, or whatever arrived within WAIT."""
        deadline = time.monotonic() + WAIT
        while True:
            got = self.record.read_text().splitlines() if self.record.exists() else []
            if (want and len(got) >= want) or time.monotonic() > deadline:
                return sorted(got)
            time.sleep(0.05)


def launched(records):
    return sorted(FAKES[r.split(" ", 1)[0]] for r in records)


def test_a_docs_only_commit_launches_none_and_says_why(tmp_path):
    r = Repo(tmp_path)
    r.commit("README.md", "wiki/topics/a.md", "todo/BUILD-TASKLIST.md", "transcripts/t.jsonl",
             "tasks/briefs/b.md", "tasks/briefs/probe.py", "docs/notes.MD")
    line = r.hook()
    assert r.records() == []                   # tasks/briefs/probe.py is code, yet tasks/ is the docs plane
    assert line.endswith(" re-index none: all 7 changed paths are Markdown or under wiki/, todo/, transcripts/, tasks/")
    assert re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ [0-9a-f]{7,} re-index ", line)


def test_a_code_commit_launches_each_graph_and_analyze_skips_agents_md(tmp_path):
    r = Repo(tmp_path)
    r.commit("README.md")
    r.hook()
    r.commit("scripts/tool.py", "README.md")
    line = r.hook()
    assert r.records(4) == sorted(["graft build", "gitnexus analyze --skip-agents-md",
                                   "codebase-memory-mcp cli index_repository --repo-path %s --mode fast" % r.top,
                                   "code-review-graph update"])
    assert line.endswith(" re-index launched: graft gitnexus codebase-memory code-review-graph")
    assert len(r.log()) == 2                   # one line per commit


@pytest.mark.parametrize("path, graphs", [
    ("scripts/run.sh", ["codebase-memory", "code-review-graph"]),
    ("data/thing.json", ["codebase-memory"]),
    ("bin/tool", ["code-review-graph"]),                          # extension-less: code-review-graph probes the shebang
    ("Makefile", ["codebase-memory", "code-review-graph"]),
    ("Rakefile", ["code-review-graph", "gitnexus"]),
    ("src/x.C", ["code-review-graph", "gitnexus", "graft"]),      # codebase-memory matches case-sensitively
])
def test_each_graph_is_launched_only_for_a_file_it_reads(tmp_path, path, graphs):
    r = Repo(tmp_path)
    r.commit(path)
    line = r.hook()
    assert launched(r.records(len(graphs))) == sorted(graphs)
    assert " re-index launched: %s" % " ".join(g for g in ALL if g in graphs) in line
    for g in ALL:
        if g not in graphs:
            assert "%s (reads none of them)" % g in line


@pytest.mark.parametrize("paths", [("harness-ports/hand-ported.sha256",), ("notes.txt", "ci/run.tsv")])
def test_a_commit_no_graph_reads_launches_none_and_names_a_path(tmp_path, paths):
    r = Repo(tmp_path)
    r.commit(*paths, "wiki/x.md")
    line = r.hook()
    assert r.records() == []
    assert line.endswith(" re-index none: no graph reads the %d changed path(s) outside the docs plane (first: %s)"
                         % (len(paths), sorted(paths)[0]))


def test_a_merge_commit_counts_the_side_it_brings_in(tmp_path):
    r = Repo(tmp_path)
    r.commit("README.md")
    base = r.git("rev-parse", "--abbrev-ref", "HEAD").strip()
    r.git("checkout", "-q", "-b", "side")
    r.commit("lib/code.py")
    r.git("checkout", "-q", base)
    r.commit("wiki/page.md")
    r.git("merge", "-q", "--no-edit", "side")
    line = r.hook()
    assert launched(r.records(4)) == sorted(ALL)
    assert line.endswith(" re-index launched: graft gitnexus codebase-memory code-review-graph")


def test_a_missing_indexer_is_named_and_the_rest_still_launch(tmp_path):
    r = Repo(tmp_path, tools=("gitnexus", "codebase-memory-mcp", "code-review-graph"))   # no graft on this PATH
    r.commit("scripts/tool.py")
    line = r.hook()
    assert launched(r.records(3)) == ["code-review-graph", "codebase-memory", "gitnexus"]
    assert line.endswith(" re-index launched: gitnexus codebase-memory code-review-graph; skipped: graft (not installed)")


# ---------- the static rule: every automatic `gitnexus analyze` passes --skip-agents-md ----------

CALL_SITES = {"scripts/hooks/post-commit": 1, "scripts/resume-heal.sh": 1, "harness-ports/bin/pc-setup.sh": 2}
ANALYZE = re.compile(r'(?:\bgitnexus|"\$bin")\s+analyze\b(.*)')    # the hook runs the resolved "$bin"


def analyze_calls(text):
    """[(line number, rest of the line after `analyze`)] for every non-comment analyze invocation."""
    out = []
    for no, ln in enumerate(text.splitlines(), 1):
        if ln.lstrip().startswith("#"):
            continue
        out += [(no, m.group(1)) for m in ANALYZE.finditer(ln)]
    return out


def test_every_automatic_analyze_call_site_passes_skip_agents_md():
    for rel, count in CALL_SITES.items():
        calls = analyze_calls((ROOT / rel).read_text(encoding="utf-8"))
        assert len(calls) == count, (rel, calls)                    # the scan saw each call site: not vacuous
        for no, rest in calls:
            assert "--skip-agents-md" in rest, "%s:%d runs analyze without --skip-agents-md" % (rel, no)


def test_negative_control_the_scan_flags_an_analyze_without_the_flag():
    planted = "# gitnexus analyze in a comment\n  ( flock -n 9 || exit 0; nohup gitnexus analyze > x.log 2>&1 ) &\n"
    calls = analyze_calls(planted)
    assert calls == [(2, " > x.log 2>&1 ) &")] and "--skip-agents-md" not in calls[0][1]
