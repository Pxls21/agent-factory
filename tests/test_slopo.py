"""INSTALL1 (D-090): slopo installed, pinned, wired and tuned; the installation table's pins.

slopo (the semantic-duplicate detector) is ADVISORY, never a gate: these tests prove its plumbing, never its clusters.
Six groups, deterministic and LLM-free:
  1. scripts/hooks/post-commit's slopo block: a commit that changed a file slopo reads (an extension slopo parses,
     under a root slopo.conf.yaml brings back) launches `scripts/slopo_review.sh --sync` in the background; a docs-only
     commit, a path outside the roots, a language slopo does not parse, or no slopo install launches nothing. The hook
     runs by hand in a throwaway repo (its commits made with hooks off) with FAKES first on PATH for every quartet
     indexer (so no real index is touched) and a fake wrapper that records its argv, as tests/test_post_commit_reindex.py
     does; the repo carries a copy of the REAL slopo.conf.yaml.
  2. scripts/slopo_review.sh: usage, not-installed and lock-busy exits; then the REAL pipeline (slopo, the embed server,
     the pinned model) on a throwaway repo: a sync embeds every unit and leaves no server running, a new near-copy of a
     function is flagged, an unrelated new function is not.
  3. scripts/slopo_embed_server.py: a text's vector does not depend on the other texts in its request, and 4 workers
     give the bit-identical vectors 1 worker gives (the tuning's correctness claim).
  4. slopo.conf.yaml's scope through slopo's own scanner: the four code roots only, no vendored or archived code;
     the negative control drops "/*/" and the scope leaks out of the roots (the pathspec trap it guards).
  5. The pins: upstream.lock.yaml, scripts/setup.sh and harness-ports/bin/pc-setup.sh name the same wheel, runtime,
     model and tool versions; the kept wheel and the model files match their digests (a flipped digest does not).
  6. .gitignore keeps slopo's local artifacts out and its config in; setup.sh's smoke() reports a missing tool and
     carries on.
Groups 2-4 and the artifact half of 5 need the slopo venv and the model (scripts/setup.sh installs both): where they are
absent (CI) those tests SKIP with the reason, by declaration; everything else runs everywhere.
"""
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "hooks" / "post-commit"
WRAPPER = ROOT / "scripts" / "slopo_review.sh"
SERVER = ROOT / "scripts" / "slopo_embed_server.py"
CONFIG = ROOT / "slopo.conf.yaml"
LOCK = ROOT / "upstream.lock.yaml"
SETUP = ROOT / "scripts" / "setup.sh"
PC_SETUP = ROOT / "harness-ports" / "bin" / "pc-setup.sh"
MODEL_DIR = ROOT / ".slopo-runtime" / "model"
VENV = Path(os.environ.get("SLOPO_VENV", str(Path.home() / "venv-slopo")))
SLOPO_PY = VENV / "bin" / "python"
WHEEL = "slopo-0.6.0-py3-none-any.whl"
FOUR_ROOTS = ["scripts", "src", "proofs", "harness-ports"]
WAIT = 10.0
HAVE_SLOPO = (VENV / "bin" / "slopo").is_file() and SLOPO_PY.is_file()
HAVE_MODEL = (MODEL_DIR / "model_quantized.onnx").is_file() and (MODEL_DIR / "tokenizer.json").is_file()
needs_slopo = pytest.mark.skipif(not HAVE_SLOPO, reason="no slopo venv at %s (scripts/setup.sh builds it)" % VENV)
needs_runtime = pytest.mark.skipif(not (HAVE_SLOPO and HAVE_MODEL),
                                   reason="no slopo venv or no model under .slopo-runtime/model (scripts/setup.sh)")


def lock():
    return yaml.safe_load(LOCK.read_text(encoding="utf-8"))


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_matches(path, pinned):
    """The pin check the artifact tests use: `pinned` is "sha256:<64 hex>" or a bare 64-hex digest."""
    want = pinned.split(":", 1)[1] if pinned.startswith("sha256:") else pinned
    return re.fullmatch(r"[0-9a-f]{64}", want) is not None and Path(path).is_file() and sha256(path) == want


def flipped(digest):
    """The same digest with its last hex digit changed: the negative control's input."""
    return digest[:-1] + ("0" if digest[-1] != "0" else "1")


# ---------- 1. the post-commit slopo block ----------

QUARTET_FAKES = ["graft", "gitnexus", "codebase-memory-mcp", "code-review-graph"]
FAKE_INDEXER = '#!/bin/sh\nexit 0\n'
FAKE_WRAPPER = '#!/bin/sh\n[ -n "$FAKE_SLEEP" ] && sleep "$FAKE_SLEEP"\nprintf \'%s cwd=%s\\n\' "$*" "$(pwd)" >> "$FAKE_RECORD"\n'


class HookRepo:
    def __init__(self, tmp_path, installed=True, config=True):
        self.root = tmp_path / "repo"
        self.bin = tmp_path / "bin"
        self.tmp = tmp_path / "t"
        self.home = tmp_path / "home"
        self.record = tmp_path / "record.txt"
        for d in (self.root / "scripts", self.bin, self.tmp, self.home):
            d.mkdir(parents=True)
        for name in QUARTET_FAKES:                       # shadow every real indexer and its fixed fallback path
            (self.bin / name).write_text(FAKE_INDEXER)
            (self.bin / name).chmod(0o755)
        wrapper = self.root / "scripts" / "slopo_review.sh"
        wrapper.write_text(FAKE_WRAPPER)
        wrapper.chmod(0o755)
        if config:
            (self.root / "slopo.conf.yaml").write_text(CONFIG.read_text(encoding="utf-8"))
        if installed:
            fake = self.home / "venv-slopo" / "bin" / "slopo"
            fake.parent.mkdir(parents=True)
            fake.write_text("#!/bin/sh\nexit 0\n")
            fake.chmod(0o755)
        self.env = {"PATH": "%s:/usr/bin:/bin" % self.bin, "HOME": str(self.home), "LC_ALL": "C",
                    "AF_POST_COMMIT_TMP": str(self.tmp), "FAKE_RECORD": str(self.record)}
        self.git("init", "-q")
        with open(self.root / ".git" / "info" / "exclude", "a") as f:
            f.write("scripts/slopo_review.sh\nslopo.conf.yaml\n")   # the fakes are never a changed path
        self.top = os.path.realpath(str(self.root))

    def git(self, *args):
        r = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "user.email=t@t", "-c", "user.name=t",
                            *args], cwd=self.root, env=self.env, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        return r.stdout

    def commit(self, *paths):
        for rel in paths:
            f = self.root / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("%s %d\n" % (rel, time.monotonic_ns()))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")

    def hook(self, **env):
        t0 = time.monotonic()
        r = subprocess.run(["bash", str(HOOK)], cwd=self.root, env={**self.env, **env}, capture_output=True,
                           text=True, timeout=60)
        self.elapsed = time.monotonic() - t0
        assert r.returncode == 0 and r.stderr == "", (r.returncode, r.stderr)
        lines = [ln for ln in self.log() if " slopo sync " in ln]
        return lines[-1] if lines else None

    def log(self):
        p = self.tmp / "slopo-sync.log"
        return p.read_text().splitlines() if p.exists() else []

    def records(self, want=0):
        deadline = time.monotonic() + WAIT
        while True:
            got = self.record.read_text().splitlines() if self.record.exists() else []
            if (want and len(got) >= want) or time.monotonic() > deadline:
                return got
            time.sleep(0.05)


def test_hook_a_code_commit_launches_the_sync_in_the_repo_root(tmp_path):
    r = HookRepo(tmp_path)
    r.commit("README.md")
    r.commit("scripts/tool.py")
    line = r.hook()
    assert r.records(1) == ["--sync cwd=%s" % r.top]
    assert re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ [0-9a-f]{7,} slopo sync launched \(first: scripts/tool\.py\)$",
                    line), line


def test_hook_a_docs_only_commit_syncs_nothing(tmp_path):
    r = HookRepo(tmp_path)
    r.commit("README.md", "wiki/topics/a.md", "todo/BUILD-TASKLIST.md", "tasks/briefs/probe.py", "scripts/notes.md")
    line = r.hook()
    assert r.records() == []                   # tasks/briefs/probe.py is Python, yet tasks/ is the docs plane
    assert line.endswith(" slopo sync none: slopo reads none of the changed paths")


@pytest.mark.parametrize("path", ["tests/test_tool.py", "docs/helper.py", "scripts/run.sh", "src/view.tsx",
                                  "scripts/data.json", "scriptsX/tool.py"])
def test_hook_a_path_slopo_does_not_read_syncs_nothing(tmp_path, path):
    r = HookRepo(tmp_path)
    r.commit(path)
    line = r.hook()
    assert r.records() == []
    assert line.endswith(" slopo sync none: slopo reads none of the changed paths")


@pytest.mark.parametrize("path", ["src/agent_factory/X.PY", "proofs/S0-01/tools/tee.py", "harness-ports/bin/a.ts",
                                  "scripts/laya_ft/fit.py"])
def test_hook_each_root_and_a_case_insensitive_extension_launch(tmp_path, path):
    r = HookRepo(tmp_path)
    r.commit(path)
    line = r.hook()
    assert r.records(1) == ["--sync cwd=%s" % r.top]
    assert line.endswith(" slopo sync launched (first: %s)" % path)


def test_hook_no_slopo_install_launches_nothing_and_says_so(tmp_path):
    r = HookRepo(tmp_path, installed=False)
    r.commit("scripts/tool.py")
    line = r.hook()
    assert r.records() == []
    assert line.endswith(" slopo sync none: slopo is not installed")


def test_hook_no_config_launches_nothing_and_says_so(tmp_path):
    r = HookRepo(tmp_path, config=False)
    r.commit("scripts/tool.py")
    line = r.hook()
    assert r.records() == []
    assert line.endswith(" slopo sync none: slopo.conf.yaml names no root")


def test_hook_the_sync_never_blocks_the_commit(tmp_path):
    r = HookRepo(tmp_path)
    r.commit("scripts/tool.py")
    line = r.hook(FAKE_SLEEP="6")
    assert r.elapsed < 5.0, r.elapsed            # the fake sync sleeps 6 s before it records
    assert "slopo sync launched" in line and not r.record.exists()
    assert r.records(1) == ["--sync cwd=%s" % r.top]              # and it did run, in the background


def test_hook_the_roots_are_the_config_s_bring_back_lines():
    roots = re.findall(r'^ *- "!/([^"/]*)/"$', CONFIG.read_text(encoding="utf-8"), flags=re.M)
    assert roots == FOUR_ROOTS                   # one root per line, in the form the hook's sed reads
    assert 'SLOPO_ROOTS="$(sed -n \'s#^ *- "!/\\([^"/]*\\)/"$#\\1#p\'' in HOOK.read_text(encoding="utf-8")


@needs_slopo
def test_hook_extension_set_is_slopo_s_own():
    hook_ext = re.search(r'^SLOPO_EXT="([^"]*)"$', HOOK.read_text(encoding="utf-8"), flags=re.M).group(1).split()
    out = subprocess.run([str(SLOPO_PY), "-c", "from slopo.indexing.parsing.registry import supported_extensions as s;"
                          "print(' '.join(sorted(e.lstrip('.') for e in s())))"],
                         capture_output=True, text=True, timeout=60, check=True).stdout.split()
    assert sorted(hook_ext) == out and len(out) == 10


# ---------- 2. scripts/slopo_review.sh ----------

def run_wrapper(*args, env=None, cwd=None, wrapper=WRAPPER, timeout=300):
    return subprocess.run(["bash", str(wrapper), *args], cwd=cwd or ROOT, env={**os.environ, **(env or {})},
                          capture_output=True, text=True, timeout=timeout)


@pytest.mark.parametrize("args", [[], ["a", "b"], ["-x"], ["--help"], [""]])
def test_wrapper_usage_exits_2(args):
    r = run_wrapper(*args)
    assert r.returncode == 2 and "usage: scripts/slopo_review.sh <base-ref> | --sync" in r.stderr


def test_wrapper_not_installed_exits_3_and_names_setup(tmp_path):
    r = run_wrapper("--sync", env={"SLOPO_VENV": str(tmp_path / "none")})
    assert r.returncode == 3 and "run scripts/setup.sh" in r.stderr and str(tmp_path / "none") in r.stderr


def fake_venv(tmp_path):
    """A venv whose slopo and python record every call: proves what the wrapper ran, touching nothing real."""
    record = tmp_path / "calls.txt"
    for name in ("slopo", "python"):
        f = tmp_path / "venv" / "bin" / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text('#!/bin/sh\necho "%s $*" >> %s\necho 0\n' % (name, record))
        f.chmod(0o755)
    return tmp_path / "venv", record


def test_wrapper_sync_skips_while_another_run_holds_the_lock(tmp_path):
    import fcntl
    venv, record = fake_venv(tmp_path)
    lockfile = tmp_path / "slopo.lock"
    with open(lockfile, "w") as held:            # held here, by this process: released when the block ends
        fcntl.flock(held, fcntl.LOCK_EX)
        assert subprocess.run(["flock", "-n", str(lockfile), "true"]).returncode == 1   # the lock is really held
        r = run_wrapper("--sync", env={"SLOPO_VENV": str(venv), "SLOPO_LOCK": str(lockfile)})
    assert r.returncode == 0 and "this sync skipped" in r.stdout
    assert not record.exists()                   # neither slopo nor python ran
    r2 = run_wrapper("--sync", env={"SLOPO_VENV": str(venv), "SLOPO_LOCK": str(lockfile)})   # the control: lock free
    assert r2.returncode == 0 and record.read_text().splitlines()[0] == "slopo index"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


DUP_A = '''def normalize_paths(items):
    out = []
    for item in items:
        text = str(item).strip().replace("\\\\", "/")
        if text and text not in out:
            out.append(text)
    return sorted(out)
'''
DUP_B = DUP_A.replace("normalize_paths", "clean_path_list")
UNRELATED = '''def parse_duration(spec):
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    total = 0
    number = ""
    for ch in spec:
        if ch.isdigit():
            number += ch
        elif ch in units and number:
            total += int(number) * units[ch]
            number = ""
        else:
            raise ValueError("bad duration: %r" % spec)
    return total
'''


class SlopoRepo:
    """A throwaway git repo carrying the real wrapper, server and config (on a free port) and the real model."""

    def __init__(self, tmp_path):
        self.root = tmp_path / "repo"
        (self.root / "scripts").mkdir(parents=True)
        for src in (WRAPPER, SERVER):
            (self.root / "scripts" / src.name).write_bytes(src.read_bytes())
        (self.root / "scripts" / WRAPPER.name).chmod(0o755)
        self.port = free_port()
        conf = CONFIG.read_text(encoding="utf-8").replace("http://127.0.0.1:8811/v1", "http://127.0.0.1:%d/v1" % self.port)
        assert conf.count(":%d/v1" % self.port) == 1
        (self.root / "slopo.conf.yaml").write_text(conf)
        (self.root / ".slopo-runtime").mkdir()
        (self.root / ".slopo-runtime" / "model").symlink_to(MODEL_DIR)
        (self.root / ".gitignore").write_text("/slopo.db\n/slopo.db-journal\n/slopo-report/\n/.slopo-runtime/\n")
        self.env = {"SLOPO_VENV": str(VENV), "SLOPO_LOCK": str(tmp_path / "slopo.lock"),
                    "SLOPO_SERVER_LOG": str(tmp_path / "server.log")}
        self.git("init", "-q")

    def git(self, *args):
        r = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "user.email=t@t", "-c", "user.name=t",
                            *args], cwd=self.root, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        return r.stdout

    def run(self, *args):
        return run_wrapper(*args, env=self.env, wrapper=self.root / "scripts" / WRAPPER.name, cwd=self.root)

    def unembedded(self):
        code = ("from pathlib import Path\nfrom slopo.config import load_config\nfrom slopo.db import open_db\n"
                "from slopo.embedding.db import count_unembedded_units\n"
                "print(count_unembedded_units(open_db(load_config(Path('slopo.conf.yaml')))))")
        return int(subprocess.run([str(SLOPO_PY), "-c", code], cwd=self.root, capture_output=True, text=True,
                                  timeout=60, check=True).stdout.strip())

    def server_up(self):
        return subprocess.run(["curl", "-fsS", "-m", "2", "http://127.0.0.1:%d/health" % self.port],
                              capture_output=True).returncode == 0


def test_wrapper_and_server_agree_on_the_token_cap():
    wrapper_cap = re.search(r"^MAX_TOKENS=(\d+)$", WRAPPER.read_text(encoding="utf-8"), flags=re.M).group(1)
    server_cap = re.search(r"^DEFAULT_MAX_TOKENS = (\d+)$", SERVER.read_text(encoding="utf-8"), flags=re.M).group(1)
    assert wrapper_cap == server_cap == "1024"


SQUATTER = r'''
import http.server, json, sys
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):                            # keyed on the path, as the real server is: /health only
        if self.path != "/health":
            self.send_response(404); self.end_headers(); return
        body = json.dumps({"status": "ok", "model": "jina-embeddings-v2-base-code-onnx-q8", "max_tokens": 4096}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        pass
http.server.HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
'''


@needs_runtime
def test_wrapper_refuses_a_server_with_another_token_cap(tmp_path):
    r = SlopoRepo(tmp_path)
    (r.root / "scripts" / "paths.py").write_text(DUP_A)
    squatter = subprocess.Popen([sys.executable, "-c", SQUATTER, str(r.port)])
    try:
        deadline = time.monotonic() + 20
        while not r.server_up():
            assert time.monotonic() < deadline and squatter.poll() is None
            time.sleep(0.05)
        out = r.run("--sync")
        assert out.returncode == 4, out.stdout + out.stderr
        assert "answers /health, but not as a jina-embeddings-v2-base-code-onnx-q8 server with max_tokens 1024" in out.stderr
        assert r.unembedded() > 0                # nothing was embedded through the squatter
        assert squatter.poll() is None           # and a server this run did not start is left alone
    finally:
        squatter.kill()
        squatter.wait()


@needs_runtime
def test_wrapper_real_pipeline_flags_a_near_copy_and_not_unrelated_code(tmp_path):
    r = SlopoRepo(tmp_path)
    (r.root / "scripts" / "paths.py").write_text(DUP_A)
    r.git("add", "-A")
    r.git("commit", "-q", "-m", "base")
    sync = r.run("--sync")
    assert sync.returncode == 0, sync.stdout + sync.stderr
    assert r.unembedded() == 0                  # the sync embedded every unit
    assert not r.server_up()                    # and stopped the server it started
    assert "Indexed" in sync.stdout and "Done" in sync.stdout

    (r.root / "scripts" / "other.py").write_text(UNRELATED)        # the negative control first: unrelated code
    neg = r.run("HEAD")
    assert neg.returncode == 0, neg.stdout + neg.stderr
    assert neg.stdout.strip().splitlines()[-1] == "No similar code involving the changes."
    (r.root / "scripts" / "other.py").unlink()

    (r.root / "scripts" / "cleanup.py").write_text(DUP_B)          # a near-copy under a new name, in a new file
    pos = r.run("HEAD")
    assert pos.returncode == 0, pos.stdout + pos.stderr
    assert pos.stdout.strip().splitlines()[-1] == "1 of 1 changed units look similar to other code."
    report = (r.root / "slopo-report" / "index.md").read_text()
    assert "cluster-1" in report.lower() or "Cluster 1" in report
    assert not r.server_up() and r.unembedded() == 0


# ---------- 3. scripts/slopo_embed_server.py ----------

@needs_runtime
def test_server_a_vector_does_not_depend_on_its_request_and_workers_are_bit_identical():
    code = r'''
import importlib.util, sys, numpy as np
from pathlib import Path
spec = importlib.util.spec_from_file_location("srv", sys.argv[1]); srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)
texts = [sys.argv[3], sys.argv[4], sys.argv[3] * 3, "def f():\n    return 1\n"]
one = srv.Embedder(Path(sys.argv[2]), 1024, 1, 1)
alone = np.array(one.embed([texts[0]])[0][0])
batch, tokens = one.embed(texts)
four = srv.Embedder(Path(sys.argv[2]), 1024, 1, 4).embed(texts)[0]
print(bool(np.array_equal(alone, np.array(batch[0]))), bool(np.array_equal(np.array(batch), np.array(four))),
      len(batch), len(batch[0]), tokens == sum(len(e.ids) for e in one.tokenizer.encode_batch(texts)))
'''
    out = subprocess.run([str(SLOPO_PY), "-c", code, str(SERVER), str(MODEL_DIR), DUP_A, UNRELATED],
                         capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, out.stderr
    assert out.stdout.split() == ["True", "True", "4", "768", "True"]


@needs_runtime
def test_server_negative_control_a_padded_run_changes_the_vector():
    """Why one text per run: padding the same text changes its int8 embedding. If this ever passes bit-equal, the
    batching rejection in the server's docstring needs a re-measure."""
    code = r'''
import sys, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
tk = Tokenizer.from_file(sys.argv[1] + "/tokenizer.json"); tk.no_padding()
s = ort.InferenceSession(sys.argv[1] + "/model_quantized.onnx", providers=["CPUExecutionProvider"])
e = tk.encode(sys.argv[2]); n = len(e.ids); pad = tk.token_to_id("<pad>")
def run(ids, mask):
    (h,) = s.run(["last_hidden_state"], {"input_ids": np.array([ids]), "attention_mask": np.array([mask])})
    m = np.array([mask])[..., None].astype(np.float32)
    return ((h * m).sum(1) / m.sum(1))[0]
a = run(e.ids, e.attention_mask); b = run(e.ids + [pad] * 64, e.attention_mask + [0] * 64)
print(bool(np.array_equal(a, b)), float(a @ b / np.linalg.norm(a) / np.linalg.norm(b)))
'''
    out = subprocess.run([str(SLOPO_PY), "-c", code, str(MODEL_DIR), DUP_A], capture_output=True, text=True,
                         timeout=300)
    assert out.returncode == 0, out.stderr
    equal, cos = out.stdout.split()
    assert equal == "False" and 0.9 < float(cos) < 1.0


def test_server_rejects_bad_flags_before_loading_anything():
    if not HAVE_SLOPO:
        pytest.skip("no slopo venv at %s (scripts/setup.sh builds it)" % VENV)
    for flags in (["--workers", "0"], ["--threads", "-1"], ["--max-tokens", "0"]):
        r = subprocess.run([str(SLOPO_PY), str(SERVER), "--model-dir", "/nonexistent", *flags],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 2 and "--workers and --max-tokens >= 1" in r.stderr, (flags, r.stderr)


# ---------- 4. the scope, through slopo's own scanner ----------

SCAN = r'''
import sys, yaml
from pathlib import Path
from slopo.indexing.scanner import scan_directory
patterns = yaml.safe_load(open(sys.argv[1]))["source_dir_exclude"]
drop = sys.argv[3] if len(sys.argv) > 3 else None
patterns = [p for p in patterns if p != drop]
for path in scan_directory(Path(sys.argv[2]), patterns):
    print(path)
'''


def scanned(drop=None):
    args = [str(SLOPO_PY), "-c", SCAN, str(CONFIG), str(ROOT)] + ([drop] if drop else [])
    return subprocess.run(args, capture_output=True, text=True, timeout=120, check=True).stdout.splitlines()


@needs_slopo
def test_scope_is_the_four_roots_without_vendored_or_archived_code():
    files = scanned()
    tops = {p.split("/")[0] for p in files}
    assert tops == set(FOUR_ROOTS), tops
    assert "scripts/slopo_embed_server.py" in files and "src/agent_factory/__init__.py" in files
    assert not [p for p in files if "/vendor/" in "/" + p or p.startswith("proofs/S0-01/tools/archive/")]


@needs_slopo
def test_scope_negative_control_without_the_dir_pattern_the_scope_leaks():
    tops = {p.split("/")[0] for p in scanned(drop="/*/")}
    assert tops - set(FOUR_ROOTS), "the scope did not leak: the control no longer shows why '/*/' is needed"
    assert {"tests", "sandbox-kit"} <= tops


# ---------- 5. the pins ----------

def assigned(text, name):
    m = re.search(r'^%s="([^"]*)"$' % re.escape(name), text, flags=re.M)
    assert m, "no %s= line" % name
    return m.group(1)


def jina_files(text):
    return dict(spec.split("=", 1) for spec in " ".join(re.findall(r'^JINA_FILES\+?="([^"]*)"$', text, flags=re.M)).split())


def pins_from(script_text):
    return {"wheel_sha": assigned(script_text, "SLOPO_WHEEL_SHA"), "wheel": assigned(script_text, "SLOPO_WHEEL"),
            "server_pins": sorted(assigned(script_text, "SLOPO_SERVER_PINS").split()),
            "jina_url": assigned(script_text, "JINA_URL"), "jina_files": jina_files(script_text)}


def lock_pins(doc):
    s, m = doc["advisory_tooling"]["slopo"], doc["advisory_models"]["jina-embeddings-v2-base-code"]
    runtime = re.findall(r"(onnxruntime|tokenizers|fastapi|uvicorn) ([0-9][0-9.]*)", s["embed_server_runtime"])
    return {"wheel_sha": s["package_wheel_digest"].split(":", 1)[1], "wheel": s["package_wheel"],
            "server_pins": sorted("%s==%s" % kv for kv in runtime),
            "jina_url": "%s/resolve/%s" % (m["checkpoint_source"], m["revision"]),
            "jina_files": {"onnx/model_quantized.onnx": m["onnx_digest"].split(":", 1)[1],
                           "tokenizer.json": m["tokenizer_digest"].split(":", 1)[1]}}


def test_pins_the_slopo_and_model_entries_parse():
    doc = lock()
    s = doc["advisory_tooling"]["slopo"]
    assert (s["package"], str(s["version"]), s["license"]) == ("slopo", "0.6.0", "AGPL-3.0-or-later")
    assert s["role"].endswith("never_a_gate") and s["package_wheel"] == WHEEL
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", s["package_wheel_digest"])
    m = doc["advisory_models"]["jina-embeddings-v2-base-code"]
    assert re.fullmatch(r"[0-9a-f]{40}", m["revision"]) and m["license"] == "Apache-2.0"
    for key in ("onnx_digest", "tokenizer_digest"):
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", m[key])
    for section in ("advisory_tooling", "advisory_models", "session_toolchain", "vendored_tooling", "container_provided"):
        for name, entry in doc[section].items():
            assert isinstance(entry, dict), (section, name)          # parse_lock requires a mapping per component
    for name in ("slopo", "jina-embeddings-v2-base-code"):
        entry = doc["advisory_tooling"].get(name) or doc["advisory_models"][name]
        assert "repository" not in entry and not [k for k in entry if k.endswith("_sha256") or k == "commit"]


def test_pins_setup_and_pc_setup_name_the_lock_s_slopo_wheel_runtime_and_model():
    want = lock_pins(lock())
    assert len(want["server_pins"]) == 4
    for script in (SETUP, PC_SETUP):
        assert pins_from(script.read_text(encoding="utf-8")) == want, script


def test_pins_negative_control_a_changed_digest_breaks_the_agreement():
    text = SETUP.read_text(encoding="utf-8")
    sha = assigned(text, "SLOPO_WHEEL_SHA")
    assert pins_from(text.replace(sha, flipped(sha))) != lock_pins(lock())


def test_pins_setup_install_lines_carry_the_session_toolchain_versions():
    doc, text = lock(), SETUP.read_text(encoding="utf-8")
    tc = doc["session_toolchain"]
    v = {k: str(e["version"]) for k, e in tc.items()}
    expected = ['"code-review-graph==%s"' % v["code-review-graph"], '"pytest==%s"' % v["pytest"],
                '"pytest-xdist==%s"' % v["pytest-xdist"], '"pyflakes==%s"' % v["pyflakes"],
                '"mcp==%s"' % v["mcp"], "@nanonets/graft@%s" % v["graft"], "gitnexus@%s" % v["gitnexus"],
                "ouroboros-ai==%s" % v["ouroboros-ai"], "releases/download/v%s" % v["codebase-memory-mcp"]]
    missing = [e for e in expected if e not in text]
    assert missing == [], missing


@needs_slopo
def test_pins_the_kept_wheel_matches_the_lock_and_is_what_is_installed():
    pinned = lock()["advisory_tooling"]["slopo"]["package_wheel_digest"]
    kept = VENV / WHEEL
    assert digest_matches(kept, pinned), "the kept wheel %s does not match the lock" % kept
    assert not digest_matches(kept, flipped(pinned))              # the negative control: a flipped digest fails
    code = r'''
import zipfile, hashlib, base64, csv, io, sys, importlib.metadata as m, pathlib
z = zipfile.ZipFile(sys.argv[1]); site = pathlib.Path(m.distribution("slopo").locate_file(""))
bad = [p for p, h, _ in csv.reader(io.StringIO(z.read("slopo-0.6.0.dist-info/RECORD").decode()))
       if h and base64.urlsafe_b64encode(hashlib.sha256((site / p).read_bytes()).digest()).rstrip(b"=").decode()
       != h.split("=", 1)[1]]
print(len(bad))
'''
    out = subprocess.run([str(SLOPO_PY), "-c", code, str(kept)], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0 and out.stdout.strip() == "0", out.stdout + out.stderr


@needs_runtime
def test_pins_the_model_files_match_the_lock():
    m = lock()["advisory_models"]["jina-embeddings-v2-base-code"]
    for name, key in (("model_quantized.onnx", "onnx_digest"), ("tokenizer.json", "tokenizer_digest")):
        assert digest_matches(MODEL_DIR / name, m[key]), name
        assert not digest_matches(MODEL_DIR / name, flipped(m[key]))


# ---------- 6. .gitignore and the smoke table ----------

def test_gitignore_keeps_slopo_artifacts_out_and_its_config_in():
    ignored = ["slopo.db", "slopo.db-journal", "slopo-report/index.md", ".slopo-runtime/model/model_quantized.onnx"]
    kept = ["slopo.conf.yaml", "slopo.ignore.txt", "scripts/slopo_review.sh", "scripts/slopo_embed_server.py"]
    r = subprocess.run(["git", "check-ignore", "--no-index", "-v", *ignored, *kept], cwd=ROOT, capture_output=True,
                       text=True, timeout=60)
    hits = {ln.split("\t", 1)[1] for ln in r.stdout.splitlines()}
    assert hits == set(ignored), hits


def slopo_ok_of(script):
    return re.search(r"^slopo_ok\(\) \{.*?^\}$", script.read_text(encoding="utf-8"), flags=re.M | re.S).group(0)


@needs_runtime
@pytest.mark.parametrize("script", [SETUP, PC_SETUP], ids=["setup.sh", "pc-setup.sh"])
def test_setup_the_present_check_passes_under_pipefail_on_the_real_venv(script):
    """Found live (INSTALL1): `slopo --version | grep -qx ...` under pipefail failed on a good venv, so every
    setup.sh run deleted and rebuilt it (about 450 MB from PyPI). The check both scripts run must pass as they run it."""
    r = subprocess.run(["bash", "-c", "set -uo pipefail\nSLOPO_VENV=%s\n%s\nslopo_ok" % (VENV, slopo_ok_of(script))],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr


def test_setup_negative_control_grep_q_under_pipefail_fails_a_matching_version(tmp_path):
    """The old shape against a producer that writes its version line, then more (slopo's echo flushes per line):
    grep -q exits at the match, the next write breaks the pipe, and pipefail fails the check. slopo_ok passes it."""
    venv = tmp_path / "venv" / "bin"
    venv.mkdir(parents=True)
    (venv / "slopo").write_text('#!/bin/sh\necho "Slopo 0.6.0"\nsleep 0.3\necho "Python 3.12.3"\n')
    (venv / "python").write_text("#!/bin/sh\nexit 0\n")
    for f in venv.iterdir():
        f.chmod(0o755)
    old = subprocess.run(["bash", "-c", 'set -uo pipefail; "%s/slopo" --version | grep -qx "Slopo 0.6.0"' % venv],
                         capture_output=True, text=True, timeout=60)
    assert old.returncode != 0
    new = subprocess.run(["bash", "-c", "set -uo pipefail\nSLOPO_VENV=%s\n%s\nslopo_ok" % (venv.parent, slopo_ok_of(SETUP))],
                         capture_output=True, text=True, timeout=60)
    assert new.returncode == 0, new.stderr


def test_setup_smoke_reports_a_missing_tool_and_carries_on():
    text = SETUP.read_text(encoding="utf-8")
    body = re.search(r"^smoke\(\) \{.*?^\}$", text, flags=re.M | re.S).group(0)
    script = ("ok() { printf 'OK %s\\n' \"$*\"; }\nwarn() { printf 'WARN %s\\n' \"$*\"; }\nSMOKE_FOUND=0; SMOKE_MISSING=0\n"
              + body + "\nsmoke present echo tool 1.2.3\nsmoke absent /nonexistent/tool --version\n"
              "smoke silent true\necho after $SMOKE_FOUND $SMOKE_MISSING\n")
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60)
    lines = r.stdout.splitlines()
    assert r.returncode == 0 and lines[-1] == "after 1 2", r.stdout
    assert re.match(r"^OK present +found +tool 1\.2\.3$", lines[0])
    assert re.match(r"^WARN absent +MISSING .*\(rc 127\)$", lines[1])
    assert re.match(r"^WARN silent +MISSING +no output \(rc 0\)$", lines[2])     # rc 0 with no output is not found
