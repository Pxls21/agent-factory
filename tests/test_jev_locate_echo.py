"""scripts/jev_locate.py and scripts/jev_echo.py end to end: fail-open with every instrument absent and with Jev down
(A2), the pack's budget at the command line (A5), --from-file, usage errors, and the echo on a fixture repo where a fix
left an unfixed sibling (tasks #227/#229, the JT2 brief).

The command-line tests run the real scripts in a subprocess over fixture repos built here with the real `git` and
`rg`; a test that needs `rg` is SKIPPED LOUDLY where ripgrep is absent (the CI runner may lack it). The loopback Jev
double answers with the Laya server's reply SHAPE and scores the test chooses; no number it returns is a model answer
(the live runs are the lane report's A1 and A4). No test calls the real endpoint or the bridge; every Jev call passes
--no-jev-log, so nothing is written to the repo's .jev/ log.
"""
import http.server
import importlib.util
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import threading

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCATE = ROOT / "scripts" / "jev_locate.py"
ECHO = ROOT / "scripts" / "jev_echo.py"
NEEDS_RG = pytest.mark.skipif(shutil.which("rg") is None,
                              reason="LOUD SKIP: ripgrep (rg) is absent here; the end-to-end locate/echo tests need it")
NEEDS_GIT = pytest.mark.skipif(shutil.which("git") is None, reason="LOUD SKIP: git is absent here")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


echo = _load("jev_echo_under_test", ECHO)
JEV_BASE = _load("jev_context_constants", ROOT / "scripts" / "jev_context.py").JEV_BASE   # the order Jev reorders


class JevDouble:
    """Routed like the real server: only POST /v1/systemone answers (AF-AP-139); scores from the test's scorer."""

    def __init__(self, scorer):
        self.requests = []
        outer = self

        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                code, obj = 404, {"error": "not found"}
                if self.path == "/v1/systemone":
                    req = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)))
                    outer.requests.append(req)
                    texts = {c["id"]: c["text"] for c in req["state"]["chunks"]}
                    answers = {q: {"type": "noul", "noul": scorer(texts[q]), "confidence": 0.9}
                               for q in req["questions"]}
                    code, obj = 200, {"model": "double", "answers": answers, "fan_out": len(answers)}
                body = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()


@pytest.fixture
def double():
    made = []

    def make(scorer):
        d = JevDouble(scorer)
        made.append(d)
        return d
    yield make
    for d in made:
        d.server.shutdown()
        d.server.server_close()


def closed_port_url():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return "http://127.0.0.1:%d" % port


def run(script, *args, env=None):
    p = subprocess.run([sys.executable, str(script)] + list(args), capture_output=True, text=True, timeout=120,
                       env=env if env is not None else dict(os.environ), cwd="/")
    return p.returncode, p.stdout, p.stderr


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                    "-c", "commit.gpgsign=false"] + list(args), check=True, capture_output=True, text=True)


def write(root, files):
    for rel, text in files.items():
        p = pathlib.Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


LOCATE_FILES = {
    "scripts/net.py": "def open_socket(path):\n    # a socket path over 108 bytes fails with OSError\n    return path\n",
    "scripts/other.py": "def unrelated():\n    return 1\n",
    "tests/test_net.py": "from net import open_socket\n\n\ndef test_open_socket():\n    assert open_socket('x')\n",
    "docs/INCIDENT-LOG.md": "| AF-AP-1 | a socket path over the limit fails | sig | inst | OPEN |\n",
    "CLAUDE.md": "**a socket path quirk: keep it short (bit 2026-09-01).**\n",
}
QUESTION = "open_socket fails with OSError when the socket path is too long"
FAST = ["--instruments", "rg,registry,quirks,git-log", "--no-jev-log"]


@pytest.fixture
def locate_repo(tmp_path):
    repo = tmp_path / "repo"
    write(repo, LOCATE_FILES)
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "init: open_socket")
    return repo


def top_lines(out):
    """The numbered item lines of the pack's top section."""
    return [ln for ln in section(out, "top") if ln[:1].isdigit() and ". " in ln]


def where(ln):
    """An item line's `path:line` (the token before the snippet's dash)."""
    return ln.split(" \u2014 ")[0].rsplit(" ", 1)[1]


def section(out, title):
    lines, keep = [], False
    for ln in out.splitlines():
        if ln.startswith("## "):
            keep = ln.startswith("## " + title)
            continue
        if keep:
            lines.append(ln)
    return lines


# ---------- A2: fail-open ----------

def test_every_instrument_absent_is_a_pack_of_unmapped_lines_and_exit_0(tmp_path):
    """PATH stripped and HOME empty over a root that HAS every index marker: each instrument fails only because its
    binary is absent (the in-process record instruments fail because their files are absent). Exit 0, one line each."""
    root, home, nobin = tmp_path / "root", tmp_path / "home", tmp_path / "no-bin"
    write(root, {"graft/INDEX.md": "x", ".gitnexus/run.cjs": "x", ".code-review-graph/graph.db": "", "scripts/a.py": "x\n"})
    home.mkdir()
    nobin.mkdir()
    # PATH names an EMPTY directory: an empty PATH string would search the current directory, and no PATH at all
    # would fall back to os.defpath (/bin:/usr/bin, where git and rg live)
    rc, out, err = run(LOCATE, QUESTION, "--root", str(root), "--order", "jev", "--jev-url", closed_port_url(),
                       "--no-jev-log", env={"PATH": str(nobin), "HOME": str(home)})
    assert rc == 0, err
    assert section(out, "unmapped") == [
        "- unmapped — graft unavailable (not found: graft)",
        "- unmapped — gitnexus query unavailable (not found: node)",
        "- unmapped — gitnexus context open_socket unavailable (not found: node)",
        "- unmapped — codebase-memory unavailable (not found: codebase-memory-mcp)",
        "- unmapped — code-review-graph callers_of open_socket unavailable (not found: code-review-graph)",
        "- unmapped — rg -F open_socket unavailable (not found: rg)",
        "- unmapped — rg -F OSError unavailable (not found: rg)",
        "- unmapped — registry unavailable (docs/INCIDENT-LOG.md absent)",
        "- unmapped — quirks unavailable (CLAUDE.md absent)",
        "- unmapped — git-log -Sopen_socket unavailable (not found: git)",
        "- unmapped — git-log -SOSError unavailable (not found: git)"]
    assert "Jev not asked: no chunks to rank (unranked)" in out and "answered: none" in out


@NEEDS_RG
@NEEDS_GIT
def test_jev_down_gives_the_unranked_pack_with_its_reason(locate_repo):
    rc, out, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "jev", "--jev-url", closed_port_url(),
                       *FAST)
    assert rc == 0, err
    assert "Jev unavailable: call 1 of 1: url: connection refused (unranked)" in out
    rc2, out2, _ = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", JEV_BASE, *FAST)
    assert [where(x) for x in top_lines(out)] == [where(x) for x in top_lines(out2)] and top_lines(out)


@NEEDS_RG
@NEEDS_GIT
def test_a_signal_free_jev_gives_the_base_pack_with_its_reason(locate_repo, double):
    """VERIFY-JT1 F-24 at the command line: every chunk scored the same (what a query over the model's window does)
    is no ranking; the pack is the base order's, with the reason."""
    d = double(lambda text: 0.4958)
    rc, out, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "jev", "--jev-url", d.url, *FAST)
    assert rc == 0, err
    assert len(d.requests) >= 1                     # Jev WAS asked; its answer carried no signal
    reasons = [ln for ln in out.split("\n") if ln.startswith("Jev unavailable: ")]
    # since D-076 (b) the Jev client refuses a signal-free batch itself; the reason is its own
    assert len(reasons) == 1 and reasons[0] == ("Jev unavailable: call 1 of 1: url: signal-free rank: all 6 chunks "
                                                "scored 0.4958 (unranked)")
    rc2, base, _ = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", JEV_BASE, *FAST)
    assert [where(x) for x in top_lines(out)] == [where(x) for x in top_lines(base)] and top_lines(out)


@NEEDS_RG
@NEEDS_GIT
def test_the_default_order_is_lexical_and_never_asks_jev(locate_repo, double):
    """D-077: with no --order the pack is the lexical order's, byte for byte, and Jev is not asked even with an
    endpoint named. The negative control: the same double IS asked under --order jev, so a default that called Jev
    would be seen here."""
    d = double(lambda text: 0.9 if "tests/test_net.py" in text else 0.1)
    rc, out, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--jev-url", d.url, *FAST)
    assert rc == 0, err
    assert d.requests == []
    assert "ranking: lexical order (lexical overlap), Jev not asked" in out.split("\n")
    rc2, lexical, _ = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "lexical", *FAST)
    assert rc2 == 0 and out == lexical
    rc3, opted, _ = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "jev", "--jev-url", d.url, *FAST)
    assert rc3 == 0 and len(d.requests) >= 1
    assert "ranking: Jev reorders the lexical order's selection" in opted


# ---------- the locator on a fixture repo ----------

@NEEDS_RG
@NEEDS_GIT
def test_locate_finds_the_files_and_records(locate_repo):
    rc, out, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "unranked", *FAST)
    assert rc == 0, err
    files = section(out, "files to read")
    assert [f.split(" ")[1].rsplit(":", 1)[0] for f in files] == ["scripts/net.py", "tests/test_net.py"]
    top = "\n".join(section(out, "top"))
    assert "registry docs/INCIDENT-LOG.md:1" in top and "quirks CLAUDE.md:1" in top
    assert "answered: rg, registry, quirks, git-log" in out
    assert "jev_locate:" in err and "wall" in err and "wall" not in out     # timing stays out of the pack


@NEEDS_RG
@NEEDS_GIT
def test_jev_order_reorders_but_never_drops_the_base_selection(locate_repo, double):
    d = double(lambda text: 0.95 if "tests/test_net.py" in text else 0.05)
    rc, out, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "jev", "--jev-url", d.url, *FAST)
    assert rc == 0, err
    assert "ranking: Jev reorders the %s order's selection" % JEV_BASE in out
    files = [f.split(" ")[1].rsplit(":", 1)[0] for f in section(out, "files to read")]
    assert files == ["tests/test_net.py", "scripts/net.py"]          # reordered by the scores
    rc, one, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "jev", "--jev-url", d.url, "--top", "1",
                       *FAST)
    rc, base, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", JEV_BASE, "--top", "1", *FAST)
    # KC-J5 at the command line: the one item shown is the base order's first, whatever Jev prefers
    assert [where(x) for x in top_lines(one)] == [where(x) for x in top_lines(base)] == ["scripts/net.py:1"]


@NEEDS_RG
@NEEDS_GIT
def test_json_pack_is_valid_and_under_budget(locate_repo):
    rc, out, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "unranked", "--json", *FAST)
    assert rc == 0, err
    d = json.loads(out)
    assert d["tool"] == "jev locate" and len(out) <= 6000
    assert [f["path"] for f in d["files"]] == ["scripts/net.py", "tests/test_net.py"]


@NEEDS_RG
@NEEDS_GIT
def test_from_file_reads_the_last_4000_characters(locate_repo, tmp_path, double):
    write(locate_repo, {"scripts/head.py": "def head_only_marker():\n    pass\n"})
    trace = tmp_path / "trace.txt"
    trace.write_text("head_only_marker was here\n" + "filler line\n" * 800 + "E   OSError: open_socket failed\n")
    d = double(lambda text: 0.5)
    rc, out, err = run(LOCATE, "--from-file", str(trace), "--root", str(locate_repo), "--order", "jev",
                       "--jev-url", d.url, *FAST)
    assert rc == 0, err
    assert "scripts/head.py" not in out and "scripts/net.py" in out           # the head is past the 4,000 tail
    assert all(r["state"]["query"].endswith("open_socket failed") for r in d.requests) and d.requests


@NEEDS_RG
@NEEDS_GIT
def test_oversized_output_stays_under_the_hard_cap(locate_repo):
    # spaced words, not one long run: the scrubber collapses a 40+ character run to `<opaque-redacted>`, and a first
    # version of this fixture was therefore never cut at all (mutant M3 survived it; the lane report, A6)
    line = "open_socket(%s)  # OSError\n" % " ".join("word%d" % j for j in range(45))
    write(locate_repo, {"scripts/big%d.py" % i: line * 60 for i in range(40)})
    rc, capped, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "unranked", "--budget", "99999",
                          "--top", "48", *FAST)
    assert rc == 0, err
    assert len(capped) <= 9000 and "budget clamped to the 9000-character hard cap" in capped
    rc, out, err = run(LOCATE, QUESTION, "--root", str(locate_repo), "--order", "unranked", "--top", "48", *FAST)
    assert rc == 0, err
    assert len(capped) > 6000 >= len(out)            # de-vacuoused: at the cap the pack is larger, so this one was cut


@pytest.mark.parametrize("args", [
    [], [QUESTION, "--from-file", "/etc/hostname"], [QUESTION, "--budget", "999"], [QUESTION, "--top", "0"],
    [QUESTION, "--top", "49"], [QUESTION, "--in", "../x"], [QUESTION, "--instruments", "graft,bogus"],
    [QUESTION, "--root", "/nonexistent/root"], [QUESTION, "--jev-timeout", "0"], ["--from-file", "/nonexistent/f"],
    ["   "], [QUESTION, "--order", "random"]])
def test_locate_usage_errors_exit_64(args):
    rc, out, err = run(LOCATE, *args)
    assert rc == 64 and out == "" and err.startswith("jev_locate: usage: ")


# ---------- the echo ----------

BEFORE = '''import os


def state_{n}(pid):
    if os.path.exists("/proc/%d/stat" % pid):
        try:
            fields = open("/proc/%d/stat" % pid).read().split()
            return fields[2]
        except (OSError, IOError):
            return "gone"
    return "gone"
'''
AFTER_A = '''import os


def state_a(pid):
    try:
        with open("/proc/%d/stat" % pid) as fh:
            return fh.read().split()[2]
    except OSError:
        return "gone"
'''
CONFIG = "import os\n\n\ndef load(cfg):\n    return os.path.exists(cfg)\n"


@pytest.fixture
def echo_repo(tmp_path):
    repo = tmp_path / "repo"
    write(repo, {"scripts/a.py": BEFORE.format(n="a"), "scripts/b.py": BEFORE.format(n="b"),
                 "scripts/c.py": CONFIG, "README.md": "doc\n"})
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "init")
    write(repo, {"scripts/a.py": AFTER_A, "README.md": "doc, changed\n"})
    git(repo, "commit", "-qam", "fix the /proc race in a.py")
    return repo


def echo_sites(out):
    return [where(ln) for ln in top_lines(out)]


@NEEDS_RG
@NEEDS_GIT
def test_echo_finds_the_unfixed_sibling_and_not_the_fixed_site(echo_repo):
    rc, out, err = run(ECHO, "--diff", "HEAD", "--root", str(echo_repo), "--order", "unranked",
                       "--instruments", "rg-token,rg-shape", "--no-jev-log")
    assert rc == 0, err
    sites = echo_sites(out)
    assert sites[0] == "scripts/b.py:5" and "scripts/c.py:5" in sites
    assert not any(s.startswith("scripts/a.py") for s in sites)                   # the fixed site is excluded
    assert [ln for ln in out.splitlines() if ln.startswith("fixed site:")] == ["fixed site: scripts/a.py:2-9"]
    assert "rg-shape+rg-token scripts/b.py:5" in out
    assert [ln for ln in section(out, "top") if ln.startswith("note:")] == [
        "note: a score is a lead, not a verdict: the BUG/WATCH/OK call on each site stays with the model (KC-J1b; a "
        "Jev score is never the only evidence)."]


@NEEDS_RG
@NEEDS_GIT
def test_the_echo_default_order_is_lexical_and_never_asks_jev(echo_repo, double):
    """D-077 for the echo: no --order gives the lexical order's sites, byte for byte, with no Jev call; the same double
    IS asked under --order jev (the negative control)."""
    d = double(lambda text: 0.95 if "scripts/c.py" in text else 0.1)
    common = ["--diff", "HEAD", "--root", str(echo_repo), "--instruments", "rg-token,rg-shape", "--no-jev-log"]
    rc, out, err = run(ECHO, *common, "--jev-url", d.url)
    assert rc == 0, err
    assert d.requests == []
    assert "ranking: lexical order (lexical overlap), Jev not asked" in out.split("\n")
    assert echo_sites(out)[0] == "scripts/b.py:5"
    rc2, lexical, _ = run(ECHO, *common, "--order", "lexical")
    assert rc2 == 0 and out == lexical
    rc3, opted, _ = run(ECHO, *common, "--order", "jev", "--jev-url", d.url)
    assert rc3 == 0 and len(d.requests) >= 1 and "ranking: Jev reorders the lexical order's selection" in opted


@NEEDS_RG
@NEEDS_GIT
def test_echo_jev_order_keeps_the_base_selection(echo_repo, double):
    d = double(lambda text: 0.95 if "scripts/c.py" in text else 0.1)
    rc, out, err = run(ECHO, "--diff", "HEAD", "--root", str(echo_repo), "--order", "jev", "--jev-url", d.url,
                       "--instruments", "rg-token,rg-shape", "--no-jev-log", "--top", "1")
    assert rc == 0, err
    assert echo_sites(out) == ["scripts/b.py:5"]        # Jev prefers c.py; it may reorder, never replace (KC-J5)
    assert "question: Does this code show the same defect as the one fixed?" in out
    q = d.requests[0]["state"]["query"]
    assert q.startswith('the defect: if os.path.exists("/proc/%d/stat" % pid):') and "; fixed as: try:" in q
    rc, out, err = run(ECHO, "--diff", "HEAD", "--root", str(echo_repo), "--order", "jev", "--jev-url", d.url,
                       "--instruments", "rg-token,rg-shape", "--no-jev-log")
    assert echo_sites(out)[:2] == ["scripts/c.py:5", "scripts/b.py:5"]      # both kept, reordered


@NEEDS_RG
@NEEDS_GIT
def test_echo_reads_a_patch_file_and_jev_down_is_unranked(echo_repo, tmp_path):
    patch = tmp_path / "fix.patch"
    patch.write_text(subprocess.run(["git", "-C", str(echo_repo), "show", "HEAD"], capture_output=True,
                                    text=True, check=True).stdout)
    rc, out, err = run(ECHO, "--diff", str(patch), "--root", str(echo_repo), "--order", "jev",
                       "--jev-url", closed_port_url(), "--instruments", "rg-token,rg-shape", "--no-jev-log")
    assert rc == 0, err
    assert "Jev unavailable: call 1 of 1: url: connection refused (unranked)" in out
    assert echo_sites(out)[0] == "scripts/b.py:5"


def test_echo_with_no_removed_code_line_has_nothing_to_echo(tmp_path):
    patch = tmp_path / "add.patch"
    patch.write_text("--- a/scripts/x.py\n+++ b/scripts/x.py\n@@ -1,1 +1,2 @@\n x = 1\n+y = 2\n")
    rc, out, err = run(ECHO, "--diff", str(patch), "--root", str(tmp_path), "--no-jev-log")
    assert rc == 0, err
    assert "nothing to echo: the diff removes no code line" in out


@pytest.mark.parametrize("args", [["--diff", "no-such-ref-xyz"], ["--diff", "-x"], [], ["--diff", "HEAD", "--top", "0"],
                                  ["--diff", "HEAD", "--instruments", "rg"]])
def test_echo_usage_errors_exit_64(args, tmp_path):
    rc, out, err = run(ECHO, *(args + ["--root", str(tmp_path)]))
    assert rc == 64 and out == "" and err.startswith("jev_echo: usage: ")


def test_parse_patch_reads_hunks_by_their_counts():
    text = ("diff --git a/q.sql b/q.sql\n--- a/q.sql\n+++ b/q.sql\n@@ -1,3 +1,2 @@\n select 1;\n"
            "--- a comment that starts with two dashes\n-select 2;\n+select 3;\n"
            "diff --git a/n.py b/n.py\nnew file mode 100644\n--- /dev/null\n+++ b/n.py\n@@ -0,0 +1 @@\n+x = 1\n")
    files = echo.parse_patch(text)
    assert [(f["path"], [(h["new_start"], h["new_len"], h["removed"], h["added"]) for h in f["hunks"]])
            for f in files] == [
        ("q.sql", [(1, 2, ["-- a comment that starts with two dashes", "select 2;"], ["select 3;"])]),
        ("n.py", [(1, 1, [], ["x = 1"])])]


def test_shape_generalizes_local_names_and_keeps_api_names():
    import re
    rx, kept = echo.shape('if os.path.exists("/proc/%d/stat" % child_pid):')
    assert rx == r'if\s+os\s*\.\s*path\s*\.\s*exists\s*\(\s*"[^"]*"\s*%\s*\w+\s*\)\s*:' and kept == 3
    assert re.search(rx, '    if os.path.exists("/proc/%d/stat" % agent_pid):')
    assert not re.search(rx, "    if os.path.isfile(x):")
    assert echo.shape('proc_state = "gone"')[1] == 0        # too generic: kept no API name, never searched
