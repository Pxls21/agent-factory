#!/usr/bin/env python3
"""Ship a session export to the PC through the bridge in verified chunks (task #252; brief
tasks/briefs/jev-laya/SESSION-EXPORT-brief.md, D-7). The coordinator runs it; its tests use a fake bridge only.

usage: ship_to_pc.py <export dir> <remote dir>

<export dir> is a finished scripts/session_export.py export. Before any call, every file its manifest.json lists must be
here with the sha256 the manifest gives, and the manifest's leak gate must read 0 (a gate that found anything is refused).
<remote dir> is an absolute path on the PC; use a fresh one per export (for example one named by the export id).

The bridge URL and token come from the repo's .pc-bridge.env (in the parent of this script's directory), read in this
process: never argv, never printed. curl gets them through `--config -` on stdin (the scripts/pc_bridge_exec.py protocol:
POST <URL>/exec, header X-Agent-Token, body {"cmd": ...}, reply {rc, stdout, stderr}, `Connection: close`, a reply that is
not JSON retried up to 3 times). curl's own error text can name the bridge link, so it is never shown.

Each file travels as chunks of 72,000 bytes: one call per chunk, carrying at most 96,000 base64 characters (one bridge
argument is limited to 131,072 bytes); up to 4 calls in flight. On the PC a chunk is decoded to a temp name and kept, as
<remote>/.ship/<file>.d/<6-digit index>, only when its sha256 equals the one the call carries; otherwise the call fails
with rc 5 and the chunk is sent again, at most 3 times in one run. When every chunk of a file is kept, one call joins them
in index order and moves the result to <remote>/<file> only when its sha256 equals the manifest's (rc 7 otherwise). A run
first lists what the PC holds -- each finished file's sha256 and each kept chunk's -- and sends only what is missing or
differs, so a rerun resumes from the chunks already verified. manifest.json ships last, and only after every file it lists
is in place: its presence on the PC means the export arrived whole.

exit: 0 every file is on the PC and verified; 2 bad input (usage, a relative remote dir, no manifest, a local file missing
      or not matching the manifest, no bridge env file); 3 the export's leak gate is not 0; 4 the bridge refused the
      token, or the PC could not be listed; 5 a chunk or a file was not verified (a rerun resumes).
Standard library only. It prints counts and file names, never the URL, the token or the remote output.
"""
import base64
import concurrent.futures
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BRIDGE_ENV = os.path.join(os.path.dirname(HERE), ".pc-bridge.env")
CHUNK = 72000                   # raw bytes per chunk: 96,000 base64 characters
B64_MAX = 96000
ARG_MAX = 131072                # the bridge runs the command as one argument
STATUS_MAX = 96000              # bytes of one listing command
IN_FLIGHT = 4
SENDS = 3                       # sends of one chunk in one run while the PC refuses it
ATTEMPTS = 3                    # requests for one call while the reply is not JSON (PC-BRIDGE.md, the poisoning quirk)
MAX_TIME = 110                  # under the bridge's ~120 s cap
STAGE = ".ship"
SHA = re.compile(r"[0-9a-f]{64}\Z")
LISTED = re.compile(r"(F|C) (\d+) (?:(\d{6}) )?([0-9a-f]{64})\Z")
REFUSED, CANNOT_WRITE, JOIN_MISMATCH, JOIN_MISSING = 5, 6, 7, 8        # the remote commands' own exit codes


class BadInput(Exception):
    pass


class GateNotClean(Exception):
    pass


class Refused(Exception):
    """The bridge answered without running the command (a wrong token): the run stops."""


class Unreachable(Exception):
    """No JSON reply after ATTEMPTS requests: the call did not run, or its answer was lost."""


def read_bridge_env(path):
    """(url, token) from a KEY=value file (the jev.py reader's rules); the values never leave this process except to
    curl's stdin."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        raise BadInput("no bridge env file (.pc-bridge.env beside scripts/)")
    vals = {}
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("export "):
            ln = ln[len("export "):].strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        vals[k.strip()] = v
    url, token = vals.get("PC_BRIDGE_URL"), vals.get("PC_BRIDGE_TOKEN")
    if not url or not token or any(c in url + token for c in '"\\\n'):
        raise BadInput("the bridge env file lacks a usable PC_BRIDGE_URL or PC_BRIDGE_TOKEN")
    return url, token


def call(cmd, url, token):
    """One command on the PC through the bridge: its envelope {rc, stdout, stderr}."""
    data = json.dumps({"cmd": cmd}).encode("utf-8")
    if len(cmd.encode("utf-8")) >= ARG_MAX:
        raise ValueError("a command of %d bytes is over the bridge's argument limit" % len(cmd.encode("utf-8")))
    fd, body = tempfile.mkstemp(prefix="ship-", suffix=".json")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)                        # the command is not secret; the token goes to curl on stdin only
        cfg = ('url = "%s/exec"\nrequest = "POST"\nheader = "Content-Type: application/json"\n'
               'header = "X-Agent-Token: %s"\nheader = "Connection: close"\ndata-binary = "@%s"\n'
               'silent\nshow-error\nmax-time = %d\n') % (url.rstrip("/"), token, body, MAX_TIME)
        for attempt in range(ATTEMPTS):
            r = subprocess.run(["curl", "--config", "-"], input=cfg, capture_output=True, text=True)
            text = r.stdout.lstrip()
            if text.startswith("{"):
                try:
                    env = json.loads(text)
                except ValueError:
                    env = None
                if isinstance(env, dict) and isinstance(env.get("rc"), int):
                    return env
                if isinstance(env, dict) and "error" in env:
                    word = str(env["error"])
                    raise Refused(word if re.fullmatch(r"[a-z ]{1,40}", word) else "an error reply")
            if attempt < ATTEMPTS - 1:
                time.sleep(1)
        raise Unreachable("curl exit %d" % r.returncode if r.returncode else "no JSON reply")
    finally:
        os.unlink(body)


def safe_rel(rel):
    return (isinstance(rel, str) and rel != "" and not rel.startswith("/") and "\\" not in rel
            and not any(ord(c) < 32 for c in rel) and rel.split("/")[0] != STAGE
            and all(p not in ("", ".", "..") for p in rel.split("/")))


def digest(path):
    """(size, sha256, [sha256 of each CHUNK]) of a local file, read once; an empty file is one empty chunk."""
    whole, chunks, size = hashlib.sha256(), [], 0
    with open(path, "rb") as fh:
        for piece in iter(lambda: fh.read(CHUNK), b""):
            whole.update(piece)
            chunks.append(hashlib.sha256(piece).hexdigest())
            size += len(piece)
    return size, whole.hexdigest(), chunks or [hashlib.sha256(b"").hexdigest()]


def plan(export_dir):
    """The files to ship, from the export's manifest, each checked here before any call; manifest.json last."""
    mpath = os.path.join(export_dir, "manifest.json")
    try:
        with open(mpath, "rb") as fh:
            m = json.loads(fh.read())
        sources = m["sources"]
        gate = m["gate"]
    except (OSError, ValueError, KeyError, TypeError):
        raise BadInput("no readable manifest.json with sources and a gate in %s" % export_dir)
    if gate.get("total") != 0 or gate.get("bad_lines") != 0:
        raise GateNotClean("the export's leak gate reads total %r, unreadable lines %r" % (gate.get("total"),
                                                                                            gate.get("bad_lines")))
    files, seen = [], set()
    for s in sources:
        rel, sha = s.get("output"), s.get("output_sha256")
        if not safe_rel(rel) or rel == "manifest.json" or rel in seen or not isinstance(sha, str) or not SHA.match(sha):
            raise BadInput("the manifest lists an unusable output entry")
        seen.add(rel)
        path = os.path.join(export_dir, rel)
        try:
            size, whole, chunks = digest(path)
        except OSError:
            raise BadInput("%s: listed in the manifest, missing here" % rel)
        if whole != sha:
            raise BadInput("%s: its sha256 is not the manifest's" % rel)
        files.append({"i": len(files), "rel": rel, "path": path, "size": size, "sha": sha, "chunks": chunks})
    size, whole, chunks = digest(mpath)
    files.append({"i": len(files), "rel": "manifest.json", "path": mpath, "size": size, "sha": whole, "chunks": chunks})
    return files


def final_path(remote, rel):
    return remote.rstrip("/") + "/" + rel


def stage_dir(remote, rel):
    return remote.rstrip("/") + "/" + STAGE + "/" + rel + ".d"


LIST_FN = ("h() { sha256sum < \"$1\" | cut -d' ' -f1; }; "
           "st() { if [ -f \"$1\" ]; then printf 'F %s %s\\n' \"$3\" \"$(h \"$1\")\"; fi; "
           "if [ -d \"$2\" ]; then for c in \"$2\"/[0-9][0-9][0-9][0-9][0-9][0-9]; do if [ -f \"$c\" ]; then "
           "printf 'C %s %s %s\\n' \"$3\" \"${c##*/}\" \"$(h \"$c\")\"; fi; done; fi; }; ")


def list_commands(files, remote):
    """The listing, in commands of at most STATUS_MAX bytes: `F <file> <sha256>` for a finished file, `C <file> <chunk>
    <sha256>` for a kept chunk."""
    cmds, cur = [], []
    for i, f in enumerate(files):
        step = "st %s %s %d; " % (shlex.quote(final_path(remote, f["rel"])), shlex.quote(stage_dir(remote, f["rel"])), i)
        if cur and len(": list; export LC_ALL=C; " + LIST_FN + "".join(cur) + step) > STATUS_MAX:
            cmds.append(cur)
            cur = []
        cur.append(step)
    cmds.append(cur)
    return [": list; export LC_ALL=C; " + LIST_FN + "".join(c) + "true" for c in cmds]


def chunk_command(remote, f, k, data):
    b64 = base64.b64encode(data).decode("ascii")
    if len(b64) > B64_MAX:
        raise ValueError("a chunk of %d base64 characters" % len(b64))
    return (": chunk %s %d; d=%s; mkdir -p \"$d\" || exit %d; t=\"$d/%06d.part.$$\"; "
            "if printf %%s '%s' | base64 -d > \"$t\" && [ \"$(sha256sum < \"$t\" | cut -d' ' -f1)\" = %s ]; "
            "then mv -f \"$t\" \"$d/%06d\" || exit %d; "
            "else rm -f \"$t\"; echo 'chunk refused: sha256 mismatch' >&2; exit %d; fi"
            ) % (shlex.quote(f["rel"]), k, shlex.quote(stage_dir(remote, f["rel"])), CANNOT_WRITE, k, b64,
                 f["chunks"][k], k, CANNOT_WRITE, REFUSED)


def join_command(remote, f):
    n = len(f["chunks"])
    return (": join %s; export LC_ALL=C; f=%s; d=%s; h() { sha256sum < \"$1\" | cut -d' ' -f1; }; "
            "if [ -f \"$f\" ] && [ \"$(h \"$f\")\" = %s ]; then rm -rf \"$d\"; exit 0; fi; "
            "mkdir -p \"$(dirname \"$f\")\" || exit %d; "
            "{ i=0; while [ \"$i\" -lt %d ]; do printf -v c '%%06d' \"$i\"; cat \"$d/$c\" || exit %d; i=$((i+1)); done; }"
            " > \"$f.part\" || exit %d; "
            "if [ \"$(h \"$f.part\")\" = %s ]; then mv -f \"$f.part\" \"$f\" && rm -rf \"$d\"; "
            "else rm -f \"$f.part\"; echo 'join refused: sha256 mismatch' >&2; exit %d; fi"
            ) % (shlex.quote(f["rel"]), shlex.quote(final_path(remote, f["rel"])),
                 shlex.quote(stage_dir(remote, f["rel"])), f["sha"], CANNOT_WRITE, n, JOIN_MISSING, CANNOT_WRITE, f["sha"],
                 JOIN_MISMATCH)


class Shipper:
    def __init__(self, files, remote, url, token):
        self.files, self.remote, self.url, self.token = files, remote, url, token
        self.lock, self.stop = threading.Lock(), threading.Event()
        self.n = {"sent": 0, "kept": 0, "refused": 0, "dropped": 0, "failed": 0, "bytes": 0}
        self.failures = []

    def _count(self, key, by=1):
        with self.lock:
            self.n[key] += by

    def _fail(self, rel, why):
        with self.lock:
            self.failures.append("%s: %s" % (rel, why))

    def listing(self):
        """({file index: sha256 of the finished file}, {file index: {chunk index: sha256}}) on the PC now."""
        finals, kept = {}, {}
        for cmd in list_commands(self.files, self.remote):
            env = call(cmd, self.url, self.token)
            if env["rc"] != 0:
                raise Unreachable("the listing ended with remote rc %d" % env["rc"])
            for line in str(env.get("stdout") or "").splitlines():
                m = LISTED.match(line.strip())
                if m and m.group(1) == "F":
                    finals[int(m.group(2))] = m.group(4)
                elif m and m.group(3) is not None:
                    kept.setdefault(int(m.group(2)), {})[int(m.group(3))] = m.group(4)
        return finals, kept

    def send(self, f, k):
        """Chunk k of file f until the PC keeps it (at most SENDS sends): True when kept."""
        with open(f["path"], "rb") as fh:
            fh.seek(k * CHUNK)
            data = fh.read(CHUNK)
        cmd = chunk_command(self.remote, f, k, data)
        for _ in range(SENDS):
            if self.stop.is_set():
                return False
            try:
                env = call(cmd, self.url, self.token)
            except Unreachable as e:
                self._count("dropped")
                self._fail(f["rel"], "chunk %d not sent (%s)" % (k, e))
                return False
            except Refused:
                self.stop.set()
                raise
            self._count("sent")
            if env["rc"] == 0:
                self._count("kept")
                self._count("bytes", len(data))
                return True
            if env["rc"] != REFUSED:
                self._fail(f["rel"], "chunk %d: remote rc %d" % (k, env["rc"]))
                return False
            self._count("refused")
        self._fail(f["rel"], "chunk %d refused %d times (sha256 mismatch on the PC)" % (k, SENDS))
        return False

    def join(self, f):
        if self.stop.is_set():
            return False
        try:
            env = call(join_command(self.remote, f), self.url, self.token)
        except Unreachable as e:
            self._fail(f["rel"], "join not sent (%s)" % e)
            return False
        except Refused:
            self.stop.set()
            raise
        if env["rc"] != 0:
            self._fail(f["rel"], "join refused: remote rc %d" % env["rc"])
            return False
        return True

    def ship(self, files, finals, kept, pool):
        """Send what the PC lacks of `files`, then join each file whose chunks are all kept: (the files now in place, how
        many of them were in place before)."""
        todo = [f for f in files if finals.get(f["i"]) != f["sha"]]
        need = [(f, k) for f in todo for k, sha in enumerate(f["chunks"]) if kept.get(f["i"], {}).get(k) != sha]
        ok = dict(zip([(f["i"], k) for f, k in need], pool.map(lambda fk: self.send(*fk), need)))
        whole = [f for f in todo if all(ok.get((f["i"], k), True) for k in range(len(f["chunks"])))]
        joined = {f["i"] for f, done in zip(whole, pool.map(self.join, whole)) if done}
        return [f for f in files if finals.get(f["i"]) == f["sha"] or f["i"] in joined], len(files) - len(todo)

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: ship_to_pc.py <export dir> <remote dir>", file=sys.stderr)
        return 2
    export_dir, remote = argv
    t0 = time.monotonic()
    try:
        if not remote.startswith("/") or remote.rstrip("/") == "" or ".." in remote.split("/") \
                or any(ord(c) < 32 for c in remote):
            raise BadInput("the remote dir must be an absolute path below / with no `..`")
        files = plan(export_dir)
        url, token = read_bridge_env(BRIDGE_ENV)
    except BadInput as e:
        print("ship_to_pc: %s" % e, file=sys.stderr)
        return 2
    except GateNotClean as e:
        print("ship_to_pc: refused: %s" % e, file=sys.stderr)
        return 3
    s = Shipper(files, remote, url, token)
    try:
        finals, kept = s.listing()
        with concurrent.futures.ThreadPoolExecutor(max_workers=IN_FLIGHT) as pool:
            placed, before = s.ship(files[:-1], finals, kept, pool)
            if len(placed) == len(files) - 1:
                last, was = s.ship(files[-1:], finals, kept, pool)        # the manifest, once every file is in place
                placed, before = placed + last, before + was
    except Refused as e:
        print("ship_to_pc: the bridge refused the request (%s); nothing more was sent" % e, file=sys.stderr)
        return 4
    except Unreachable as e:
        print("ship_to_pc: the PC could not be listed (%s)" % e, file=sys.stderr)
        return 4
    for line in sorted(s.failures):
        print("ship_to_pc: %s" % line, file=sys.stderr)
    print("files %d: in place %d (already there %d), not verified %d" % (len(files), len(placed), before,
                                                                        len(files) - len(placed)))
    print("chunks: sent %d, kept %d, refused %d, dropped %d; %d bytes kept; %.1f s" % (
        s.n["sent"], s.n["kept"], s.n["refused"], s.n["dropped"], s.n["bytes"], time.monotonic() - t0))
    if len(placed) < len(files):
        print("ship_to_pc: incomplete; the manifest %s; run the same command again to resume" % (
            "is on the PC" if files[-1] in placed else "was not sent"), file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
