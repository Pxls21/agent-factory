"""scripts/ship_to_pc.py against a fake bridge (task #252; brief tasks/briefs/jev-laya/SESSION-EXPORT-brief.md, D-7): every
file of a real session_export.py export arrives whole, in chunks of at most 96,000 base64 characters with at most 4 calls
in flight, and the manifest last; a dropped chunk resumes from the chunks already verified; a corrupted chunk is refused
on the PC; a wrong token is refused; a bad export is refused before any call. The shipper reads .pc-bridge.env from the
parent of its own directory, and the repo's would point at the LIVE bridge, so every test runs a copy of ship_to_pc.py
in a temp tree whose .pc-bridge.env names the fake (the tests/test_pc_sh.py pattern). The fake runs each command with
bash in a temp dir that stands for the PC."""
import hashlib
import http.server
import json
import os
import random
import re
import shutil
import string
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "fake-ship-token-not-real"
SID = "0f0f0f0f-fake-4a4a-8b8b-00000000beef"
BIG = "-home-user/%s.jsonl.xz" % SID                  # the export's largest file: several chunks
MARK = re.compile(r": (list|chunk|join)(?: (\S+))?(?: (\d+))?;")
B64 = re.compile(r"printf %s '([^']*)'")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _transcript(path, proj, n_text, rng):
    """A transcript in the harness's record shape (compact JSON): an owner turn, then assistant text of random words
    (no digits, no punctuation: no secret shape, and it barely compresses)."""
    recs = [{"type": "user", "cwd": str(proj), "sessionId": SID, "uuid": "u-0", "timestamp": "2026-09-25T01:00:00.000Z",
             "message": {"role": "user", "content": "ship this"}, "origin": {"kind": "human"}}]
    for i in range(n_text):
        words = " ".join("".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(3, 9)))
                         for _ in range(4000))                        # about 28,000 characters: under the cap
        recs.append({"type": "assistant", "cwd": str(proj), "sessionId": SID, "uuid": "u-%d" % (i + 1),
                     "timestamp": "2026-09-25T01:00:%02d.000Z" % (i + 1),
                     "message": {"model": "claude-fake", "role": "assistant", "stop_reason": "end_turn",
                                 "content": [{"type": "text", "text": words}]}})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in recs))


@pytest.fixture(scope="module")
def export(tmp_path_factory):
    """A real export (scripts/session_export.py, its own key) of three transcripts in two project folders."""
    base = tmp_path_factory.mktemp("ship-export")
    tree, rng = base / "projects", random.Random(252)
    _transcript(tree / BIG[:-3], base / "proj", 16, rng)
    _transcript(tree / ("-home-user/%s/subagents/agent-azqship1.jsonl" % SID), base / "proj", 1, rng)
    _transcript(tree / ("-home-user-agent-factory/%s.jsonl" % SID), base / "proj", 1, rng)
    tool = str(ROOT / "scripts" / "session_export.py")
    key = base / "cfg" / "pseudonym.key"
    r = subprocess.run([sys.executable, tool, "init-key", "--key", str(key)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-2000:]
    out = base / "export"
    r = subprocess.run([sys.executable, tool, "export", "--root", str(tree), "--out", str(out), "--jobs", "1",
                        "--key", str(key)], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    m = json.loads((out / "manifest.json").read_text())
    big = [s for s in m["sources"] if s["output"] == BIG][0]
    assert len(m["sources"]) == 3 and big["output_bytes"] > 3 * 72000, big["output_bytes"]
    return out


class FakePC:
    """The bridge's stand-in: POST /exec with the token runs the command with bash here, as the bridge does on the PC,
    and answers {rc, stdout, stderr}; anything else gets {"error": "forbidden"}. `drop` holds (file, chunk) calls that
    get a gateway page and never run; `corrupt` maps (file, chunk) to how many of its sends get one base64 character
    changed before they run. Every call is logged as (kind, file, chunk, rc)."""

    def __init__(self):
        self.lock = threading.Lock()
        self.log, self.drop, self.corrupt = [], set(), {}
        self.sizes, self.b64, self.in_flight, self.max_in_flight = [], [], 0, 0

    def handle(self, path, token, body):
        req = json.loads(body or b"{}")
        if path != "/exec" or token != TOKEN or not isinstance(req.get("cmd"), str):
            with self.lock:
                self.log.append(("forbidden", None, None, None))
            return 403, {"error": "forbidden"}
        cmd = req["cmd"]
        m = MARK.match(cmd)
        kind, rel, k = (m.group(1), m.group(2), int(m.group(3)) if m.group(3) else None) if m else ("other", None, None)
        with self.lock:
            self.in_flight += 1
            self.max_in_flight = max(self.max_in_flight, self.in_flight)
            self.sizes.append(len(cmd.encode()))
            self.b64.extend(len(b) for b in B64.findall(cmd))
            if (rel, k) in self.drop:
                self.log.append((kind, rel, k, "dropped"))
                self.in_flight -= 1
                return 502, None
            if self.corrupt.get((rel, k), 0) > 0:
                self.corrupt[(rel, k)] -= 1
                b = B64.search(cmd)
                i = b.start(1) + len(b.group(1)) // 2
                cmd = cmd[:i] + ("B" if cmd[i] == "A" else "A") + cmd[i + 1:]
        try:
            if len(cmd.encode()) >= 131072:
                rc, out, err = 126, "", "Argument list too long"
            else:
                time.sleep(0.05 if kind == "chunk" else 0)          # a PC call takes time: the calls overlap
                r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=60)
                rc, out, err = r.returncode, r.stdout, r.stderr
            with self.lock:
                self.log.append((kind, rel, k, rc))
            return 200, {"rc": rc, "stdout": out, "stderr": err}
        finally:
            with self.lock:
                self.in_flight -= 1

    def calls(self, kind):
        return [(rel, k, rc) for kd, rel, k, rc in self.log if kd == kind]


@pytest.fixture
def pc(tmp_path):
    """(run, fake, remote): run(export dir, remote dir, token=TOKEN, env_file=True) runs a copy of the shipper whose
    .pc-bridge.env names the fake."""
    fake = FakePC()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            status, reply = fake.handle(self.path, self.headers.get("X-Agent-Token"), body)
            data = (b"<html><body>502 Bad gateway</body></html>" if reply is None
                    else json.dumps(reply).encode())
            self.send_response(status)
            self.send_header("Content-Type", "text/html" if reply is None else "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d" % server.server_address[1]
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(ROOT / "scripts" / "ship_to_pc.py", repo / "scripts" / "ship_to_pc.py")
    env = {k: v for k, v in os.environ.items() if k.lower() not in ("http_proxy", "https_proxy", "all_proxy")}
    env.update(NO_PROXY="127.0.0.1", no_proxy="127.0.0.1")

    def run(export_dir, remote, token=TOKEN, env_file=True):
        envf = repo / ".pc-bridge.env"
        if env_file:
            envf.write_text('# the fake bridge\nexport PC_BRIDGE_URL=%s\nPC_BRIDGE_TOKEN="%s"\n' % (url, token))
        elif envf.exists():
            envf.unlink()
        r = subprocess.run([sys.executable, str(repo / "scripts" / "ship_to_pc.py"), str(export_dir), str(remote)],
                           capture_output=True, text=True, env=env, timeout=300)
        said = r.stdout + r.stderr
        assert TOKEN not in said and url not in said and "127.0.0.1" not in said, "the shipper printed the token or URL"
        return r

    yield run, fake, tmp_path / "pc" / "exports" / "run-1"
    server.shutdown()


def _arrived(export, remote):
    """Names of the manifest's files (and the manifest) whose copy on the PC is missing or differs."""
    m = json.loads((export / "manifest.json").read_text())
    bad = [s["output"] for s in m["sources"] if not (remote / s["output"]).is_file() or _sha(remote / s["output"])
           != s["output_sha256"]]
    if not (remote / "manifest.json").is_file() or _sha(remote / "manifest.json") != _sha(export / "manifest.json"):
        bad.append("manifest.json")
    return bad


def _staged(remote, rel):
    d = remote / ".ship" / (rel + ".d")
    return sorted(p.name for p in d.iterdir()) if d.is_dir() else []


def test_every_file_arrives_whole_in_bounded_chunks_and_the_manifest_last(export, pc):
    run, fake, remote = pc
    r = run(export, remote)
    assert r.returncode == 0, r.stderr[-2000:]
    assert _arrived(export, remote) == []
    assert "files 4: in place 4 (already there 0), not verified 0" in r.stdout
    assert [p for p in (remote / ".ship").rglob("*") if p.is_file()] == []           # every staged chunk cleaned up
    n_big = -(-(export / BIG).stat().st_size // 72000)
    assert sorted(k for rel, k, rc in fake.calls("chunk") if rel == BIG) == list(range(n_big)) and n_big >= 4
    assert max(fake.b64) == 96000 and max(fake.sizes) < 131072
    assert 2 <= fake.max_in_flight <= 4, fake.max_in_flight
    kinds = [(kd, rel) for kd, rel, k, rc in fake.log]
    first_manifest = kinds.index(("chunk", "manifest.json"))
    assert kinds[0] == ("list", None) and kinds[-1] == ("join", "manifest.json")
    assert all(i < first_manifest for i, (kd, rel) in enumerate(kinds) if kd == "join" and rel != "manifest.json")
    assert sorted(rel for kd, rel in kinds if kd == "join") == sorted(
        [s["output"] for s in json.loads((export / "manifest.json").read_text())["sources"]] + ["manifest.json"])
    # a rerun finds everything in place and sends nothing
    before = len(fake.log)
    r2 = run(export, remote)
    assert r2.returncode == 0 and "in place 4 (already there 4)" in r2.stdout, r2.stderr[-2000:]
    assert [kd for kd, rel, k, rc in fake.log[before:]] == ["list"]


def test_a_dropped_chunk_resumes_from_the_verified_chunks(export, pc):
    run, fake, remote = pc
    fake.drop = {(BIG, 1)}
    r1 = run(export, remote)
    assert r1.returncode == 5 and "chunk 1 not sent (no JSON reply)" in r1.stderr, r1.stderr[-2000:]
    assert "the manifest was not sent" in r1.stderr
    assert fake.calls("chunk").count((BIG, 1, "dropped")) == 3                        # the call's three attempts
    assert _arrived(export, remote) == [BIG, "manifest.json"]
    n_big = -(-(export / BIG).stat().st_size // 72000)
    assert _staged(remote, BIG) == ["%06d" % k for k in range(n_big) if k != 1]
    assert [rel for rel, k, rc in fake.calls("chunk")].count("manifest.json") == 0
    fake.drop = set()
    before = len(fake.log)
    r2 = run(export, remote)
    assert r2.returncode == 0, r2.stderr[-2000:]
    again = [(kd, rel, k) for kd, rel, k, rc in fake.log[before:]]
    assert again == [("list", None, None), ("chunk", BIG, 1), ("join", BIG, None), ("chunk", "manifest.json", 0),
                     ("join", "manifest.json", None)]
    assert _arrived(export, remote) == []


def test_a_corrupted_chunk_is_refused_on_the_pc(export, pc, tmp_path):
    run, fake, remote = pc
    fake.corrupt = {(BIG, 2): 1}                                     # once: the PC refuses it, the second send is kept
    r = run(export, remote)
    assert r.returncode == 0 and "refused 1" in r.stdout, r.stderr[-2000:]
    assert [rc for rel, k, rc in fake.calls("chunk") if (rel, k) == (BIG, 2)] == [5, 0]
    assert _arrived(export, remote) == []
    # every send corrupted: the chunk is never kept, the file never joined, the manifest never sent
    other = tmp_path / "pc" / "exports" / "run-2"
    fake.corrupt = {(BIG, 2): 99}
    before = len(fake.log)
    r = run(export, other)
    assert r.returncode == 5 and "chunk 2 refused 3 times" in r.stderr, r.stderr[-2000:]
    later = fake.log[before:]
    assert [rc for kd, rel, k, rc in later if (kd, rel, k) == ("chunk", BIG, 2)] == [5, 5, 5]
    assert "000002" not in _staged(other, BIG) and not [p for p in _staged(other, BIG) if ".part" in p]
    assert _arrived(export, other) == [BIG, "manifest.json"]
    assert not [1 for kd, rel, k, rc in later if rel == "manifest.json" or (kd, rel) == ("join", BIG)]


def test_a_wrong_token_is_refused(export, pc):
    # negative control for the stand-in too: it runs nothing for a request the real bridge would refuse
    run, fake, remote = pc
    r = run(export, remote, token="another-fake-token")
    assert r.returncode == 4 and "the bridge refused the request (forbidden)" in r.stderr, r.stderr[-2000:]
    assert "another-fake-token" not in r.stdout + r.stderr
    assert {kd for kd, rel, k, rc in fake.log} == {"forbidden"} and not remote.exists()


def test_a_bad_export_is_refused_before_any_call(export, pc, tmp_path):
    run, fake, remote = pc

    def copy(name, edit=None):
        d = tmp_path / name
        shutil.copytree(export, d)
        if edit:
            m = json.loads((d / "manifest.json").read_text())
            edit(m, d)
            (d / "manifest.json").write_text(json.dumps(m))
        return d

    def gate_found(m, d):
        m["gate"]["total"] = 1

    def outside(m, d):
        m["sources"][0]["output"] = "../outside.xz"

    changed = copy("changed")
    raw = bytearray((changed / BIG).read_bytes())
    raw[100] ^= 1
    (changed / BIG).write_bytes(bytes(raw))
    missing = copy("missing")
    (missing / BIG).unlink()
    cases = [(copy("gate", gate_found), str(remote), True, 3, "leak gate reads total 1"),
             (changed, str(remote), True, 2, "its sha256 is not the manifest's"),
             (missing, str(remote), True, 2, "listed in the manifest, missing here"),
             (copy("outside", outside), str(remote), True, 2, "unusable output entry"),
             (export, "relative/dir", True, 2, "must be an absolute path"),
             (export, "/", True, 2, "must be an absolute path"),
             (export, str(remote) + "/../up", True, 2, "must be an absolute path"),
             (export, str(remote), False, 2, "no bridge env file")]
    got = []
    for d, where, env_file, rc, words in cases:
        r = run(d, where, env_file=env_file)
        got.append((r.returncode, words in r.stderr))
    assert got == [(rc, True) for _, _, _, rc, _ in cases], got
    assert fake.log == [] and not remote.exists()
