#!/usr/bin/env python3
"""codemap.py — the code-map cache of System 1 (D-090, design L2): one pack per code file, its builder, its reader.

The instruments cost 0.2-4.8 s a call, so no hook can run them on an edit. They run after a commit, here, and write one
JSON pack per code file under `.jev/codemap/<path>.json`; the PreToolUse hook (L2b) reads a pack in milliseconds.

A pack describes ONE content of the file (its git blob and sha256) and holds:
  - the file's symbols and their line spans: graft `skeleton` (code-review-graph `file_summary` for a file type graft
    does not parse, such as shell), each with the decorators above it from the file's own AST (Python);
  - per symbol, its direct callers (a count and up to three `file:line`, from one GitNexus Cypher per file) and
    GitNexus's risk (`impact`, upstream, its default depth, tests excluded): the file's `impact` calls are pipelined
    into ONE `gitnexus mcp` session per build (measured 5-6x cheaper than one CLI call per symbol, the same risk);
  - the tests that cover the file (code-review-graph `tests_for` on the file);
  - the registry rows the file's lines match (`scripts/ap_screen.py`, in process, with each row's message).
Each graph section records whether that graph was built from exactly these bytes: graft, GitNexus and
code-review-graph each keep the sha256 of every file they indexed. A missing instrument is named as missing (absent,
no-index, n/a, error), never filled in (the NO STUBS rule). GitNexus risk UNKNOWN means it resolved no caller: the pack
keeps it as unresolved, never as "no callers".

Usage:
  codemap.py build [--all] [PATH...]        build the packs now, from the graphs as they are
  codemap.py refresh --commit SHA --lock-dir DIR [--graphs "graft gitnexus ..."] [--wait S] [--grace S] -- PATH...
      the post-commit refresh: wait until each graph re-indexed for this commit is idle and has indexed each file's
      current bytes, then build; prints one result line
  codemap.py lookup PATH --line N [--end-line M] [--json]
  codemap.py demo PAYLOAD.json|-            what L2b would inject for a recorded Edit payload (file_path, old_string)
Python (the hook): lookup(path, line, end_line=None, root=None) and edit_context(file_path, old_string, root=None).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = Path(".jev") / "codemap"
SCHEMA = 1
TEXT_CAP = 1500                     # bytes of entry text; the hook adds its label and pointer inside its 2,048
PREFIXES = ("scripts/", "src/", "proofs/", "spikes/", "harness-ports/")
SAMPLE = 3                          # callers and tests named per entry
LANG = {"py": "python", "pyi": "python", "sh": "shell", "bash": "shell", "js": "javascript", "mjs": "javascript",
        "cjs": "javascript", "jsx": "javascript", "ts": "typescript", "tsx": "typescript", "mts": "typescript",
        "cts": "typescript"}
GRAPHS = ("graft", "gitnexus", "code-review-graph")
# Which graph parses which of the LANG file types ("" = no extension): the post-commit hook's read-sets (GRAFT_EXT,
# GITNEXUS_EXT, CRG_EXT) restricted to LANG. tests/test_codemap.py holds them equal to the hook's.
READS = {"graft": {"py", "pyi", "js", "mjs", "cjs", "jsx", "ts", "tsx", "mts", "cts"},
         "gitnexus": {"py", "js", "mjs", "cjs", "jsx", "ts", "tsx", "mts", "cts"},
         "code-review-graph": {"py", "sh", "bash", "js", "mjs", "jsx", "ts", "tsx", ""}}
LOCKS = {"graft": "graft-build.lock", "gitnexus": "gitnexus-analyze.lock", "code-review-graph": "crg-build.lock"}
CRG_FALLBACK = "/root/venv-crg/bin/code-review-graph"     # the hook's fixed fallback path
Q_SYMBOLS = ("MATCH (n) WHERE n.filePath = $f AND label(n) IN ['Function', 'Method', 'Class', 'Interface', "
             "'Constructor'] RETURN {id: n.id, name: n.name, kind: label(n), s: n.startLine, e: n.endLine} AS row")
Q_CALLERS = ("MATCH (a)-[r:CodeRelation]->(b) WHERE b.filePath = $f AND r.type = 'CALLS' "
             "RETURN {callee: b.id, name: a.name, kind: label(a), file: a.filePath, line: a.startLine} AS row")
UNRESOLVED = ("unresolved, not zero: GitNexus resolved no caller outside tests; a dynamic call, getattr, a callback, "
              "an argparse type= or a module run by path leaves no edge. Confirm with: grep -rnw '%s' .")


# ---------- paths, languages, hashes ----------

def _ext(rel: str) -> str:
    """The extension the post-commit hook reads: after the last dot of a basename with a character before it."""
    b = rel.rsplit("/", 1)[-1]
    return b.rsplit(".", 1)[1].lower() if "." in b[1:] else ""


def rel_path(root: Path, path) -> str | None:
    """`path` (absolute, or relative to the root) as a repo-relative POSIX path; None outside the root."""
    p = Path(path)
    p = p if p.is_absolute() else Path(root) / p
    try:
        return Path(os.path.normpath(p)).relative_to(os.path.normpath(root)).as_posix()
    except ValueError:
        return None


def language(root: Path, rel: str) -> str | None:
    e = _ext(rel)
    if e:
        return LANG.get(e)
    try:
        with open(Path(root) / rel, "rb") as f:
            head = f.readline(200)
    except OSError:
        return None
    if head.startswith(b"#!"):
        if b"python" in head:
            return "python"
        if re.search(rb"[/ ](?:ba)?sh\b", head):
            return "shell"
    return None


def in_scope(rel: str | None) -> bool:
    return bool(rel) and rel.startswith(PREFIXES) and not rel.lower().endswith((".md", ".mdx", ".markdown"))


def reads(graph: str, rel: str) -> bool:
    return _ext(rel) in READS[graph]


def blob_sha(data: bytes) -> str:
    """git's blob id of these bytes (what `git hash-object --no-filters` prints)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def pack_path(root: Path, rel: str) -> Path:
    return Path(root) / PACK_DIR / (rel + ".json")


def _is_test(rel: str | None) -> bool:
    if not rel:
        return False
    b = rel.rsplit("/", 1)[-1]
    return rel.startswith("tests/") or "/tests/" in rel or b.startswith("test_") or b.endswith("_test.py") \
        or b == "conftest.py"


# ---------- the graphs' own freshness records, read only ----------

def stamp(graph: str, root: Path, rel: str) -> str | None:
    """The sha256 of `rel` as `graph` last indexed it, from the graph's own record; None when it has none or the record
    cannot be read (never a guess)."""
    root = Path(root)
    try:
        if graph == "gitnexus":
            v = json.loads((root / ".gitnexus" / "meta.json").read_text(encoding="utf-8"))["fileHashes"].get(rel)
            return v if isinstance(v, str) else None
        if graph == "graft":
            fps = sorted((root / "graft" / ".cache").glob("fingerprint.*.json"), key=lambda p: p.stat().st_mtime)
            if not fps:
                return None
            v = json.loads(fps[-1].read_text(encoding="utf-8"))["files"].get(rel)
            return v[2] if isinstance(v, list) and len(v) > 2 and isinstance(v[2], str) else None
        if graph == "code-review-graph":
            import sqlite3
            db = root / ".code-review-graph" / "graph.db"
            if not db.is_file():
                return None
            con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
            try:
                row = con.execute("SELECT file_hash FROM nodes WHERE kind = 'File' AND file_path = ?",
                                  (os.path.realpath(root / rel),)).fetchone()
            finally:
                con.close()
            return row[0] if row and isinstance(row[0], str) else None
    except Exception:          # a missing, locked or reshaped record is "unknown", which never counts as fresh
        return None
    raise ValueError("unknown graph %r" % graph)


def lock_held(path: Path) -> bool | None:
    """True while a process holds a flock on `path`, read from /proc/locks WITHOUT taking the lock (taking it, even for
    an instant, would make a re-index starting at that instant skip its `flock -n`). None when unreadable."""
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return False
    except OSError:
        return None
    try:
        text = Path("/proc/locks").read_text()
    except OSError:
        return None
    want = (os.major(st.st_dev), os.minor(st.st_dev), st.st_ino)
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 3 or parts[1] == "->" or "FLOCK" not in parts:   # "->" marks a waiter, not a holder
            continue
        for tok in parts:
            bits = tok.split(":")
            if len(bits) == 3:
                try:
                    if (int(bits[0], 16), int(bits[1], 16), int(bits[2])) == want:
                        return True
                except ValueError:
                    pass
    return False


def wait_for_graphs(root: Path, rels, graphs, lock_dir: Path, wait: float = 1200.0, grace: float = 30.0,
                    poll: float = 1.0):
    """The refresh's ordering: block until every graph in `graphs` (the re-indexes the post-commit hook launched for this
    commit) is idle and has indexed the current bytes of every file of `rels` it parses.

    A graph is ready when its re-index lock is not held and its own per-file sha256 equals the file's. While the lock is
    held, wait (up to `wait` seconds in all). When the lock is free but the graph has not indexed the bytes, wait `grace`
    seconds from the last time the lock was seen held (or from the start), which covers a re-index launched but not yet
    holding its lock; after that no re-index is coming for these bytes (it was skipped, or failed) and the refresh goes
    on with that graph marked stale in the packs. Returns ({graph: why it was not ready}, seconds waited, notes)."""
    import time
    root, lock_dir = Path(root), Path(lock_dir)
    need = {}
    for g in GRAPHS:
        if g in graphs:
            files = [r for r in rels if reads(g, r) and (root / r).is_file()]
            if files:
                need[g] = files
    start = time.monotonic()
    busy_at = dict.fromkeys(need, start)
    notes = set()
    while True:
        now = time.monotonic()
        state, open_ = {}, False
        for g, files in need.items():
            held = lock_held(lock_dir / LOCKS[g])
            if held is None:
                notes.add("the lock state of %s was unreadable (only its record was checked)" % g)
            if held:
                busy_at[g] = now
                state[g], open_ = "its re-index was still running", True
                continue
            behind = [r for r in files if stamp(g, root, r) != _sha256_file(root / r)]
            if behind:
                state[g] = "it had not indexed %s%s" % (behind[0], " (+%d more)" % (len(behind) - 1)
                                                        if len(behind) > 1 else "")
                if now - busy_at[g] < grace:
                    open_ = True
        if not open_ or now - start >= wait:
            return {g: why for g, why in state.items()}, now - start, sorted(notes)
        time.sleep(poll)


# ---------- the instruments ----------

def _run(argv, root, env, timeout):
    import subprocess
    try:
        return subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return "timed out after %d s" % timeout
    except OSError as e:
        return "could not run: %s" % e


def _which(name, env, fallback=None):
    import shutil
    exe = shutil.which(name, path=env.get("PATH", ""))
    if exe:
        return exe
    return fallback if fallback and os.access(fallback, os.X_OK) else None


def _fresh(indexed, sha) -> str:
    return "not-indexed" if indexed is None else ("fresh" if indexed == sha else "stale")


def _span(text):
    m = re.fullmatch(r"L(\d+)-L(\d+)", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def _graft(root, rel, sha, env):
    if not reads("graft", rel):
        return {"status": "n/a", "note": "graft does not parse this file type"}, []
    exe = _which("graft", env)
    if not exe:
        return {"status": "absent", "note": "graft is not installed (not on PATH)"}, []
    if not (Path(root) / "graft" / ".graph" / "wiring.json").is_file():
        return {"status": "no-index", "note": "graft/ holds no graph (run `graft build`)"}, []
    sec = {"status": "ok", "graph": _fresh(stamp("graft", root, rel), sha), "indexed_sha256": stamp("graft", root, rel)}
    r = _run([exe, "skeleton", "--json", "--no-refresh", rel], root, dict(env, DO_NOT_TRACK="1"), 120)
    if isinstance(r, str) or r.returncode != 0:
        return dict(sec, status="error", note=(r if isinstance(r, str) else "rc %d: %s" % (
            r.returncode, (r.stderr or r.stdout).strip()[-200:]))), []
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return dict(sec, status="error", note="skeleton printed no JSON: %s" % r.stdout[:120]), []
    syms, bad = [], 0
    for e in d.get("entries") or []:
        sp = _span(e.get("span"))
        if not sp or not e.get("name"):
            bad += 1
            continue
        syms.append({"name": e["name"], "kind": (e.get("kind") or "symbol").lower(), "start": sp[0], "end": sp[1],
                     "signature": " ".join((e.get("signature") or "").split())[:160]})
    if bad:
        sec["unparsed_entries"] = bad
    if not syms:
        sec.update(status="no-data", note=d.get("note") or "no definitions indexed for this file")
    return sec, syms


class GitNexus:
    """One `gitnexus mcp` stdio session for a whole build; a file's calls are pipelined into it (at most WINDOW in
    flight). Every call names the repo by path: omitted, the server answers from whichever single repo is registered,
    which can be another checkout (measured). Reads the raw pipe with its own line buffer, since select() on a
    buffered text stream misses lines already read into the buffer. After one failed batch (a timeout, an exit) the
    session is dead and every later call fails at once, so a hung server costs one timeout per build, not one per
    file while the refresh holds its lock."""
    WINDOW = 16

    def __init__(self, exe, root, timeout=300.0):
        import subprocess
        self.root, self.timeout, self.n, self.buf, self.dead = str(root), timeout, 0, b"", None
        self.p = subprocess.Popen([exe, "mcp"], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, bufsize=0)
        first = self._batch([("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                             "clientInfo": {"name": "codemap", "version": "1"}})])[0]
        if "result" not in first:
            raise RuntimeError("gitnexus mcp refused initialize: %s" % json.dumps(first)[:200])
        self._send(None, "notifications/initialized", {})

    def _send(self, i, method, params):
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        if i is not None:
            msg["id"] = i
        self.p.stdin.write((json.dumps(msg) + "\n").encode())

    def _line(self, deadline):
        import select
        import time
        while b"\n" not in self.buf:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError("gitnexus mcp gave no answer within %.0f s" % self.timeout)
            ready, _, _ = select.select([self.p.stdout], [], [], min(1.0, left))
            if ready:
                chunk = os.read(self.p.stdout.fileno(), 1 << 16)
                if not chunk:
                    raise EOFError("gitnexus mcp exited (rc %s)" % self.p.poll())
                self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return line

    def _batch(self, reqs):
        if self.dead:
            raise EOFError("the gitnexus mcp session failed earlier in this build (%s)" % self.dead)
        try:
            return self._pipelined(reqs)
        except (OSError, EOFError, TimeoutError) as e:
            self.dead = "%s: %s" % (type(e).__name__, str(e)[:120])
            raise

    def _pipelined(self, reqs):
        import time
        deadline = time.monotonic() + self.timeout
        out, pending, queue = [None] * len(reqs), {}, list(enumerate(reqs))
        while queue or pending:
            while queue and len(pending) < self.WINDOW:
                k, (method, params) = queue.pop(0)
                self.n += 1
                pending[self.n] = k
                self._send(self.n, method, params)
            try:
                msg = json.loads(self._line(deadline))
            except ValueError:
                continue
            if isinstance(msg, dict) and msg.get("id") in pending:
                out[pending.pop(msg["id"])] = msg
        return out

    def tools(self, calls):
        """[(tool, args)] -> [(value, None) | (None, error text)], in order."""
        res = []
        for msg in self._batch([("tools/call", {"name": t, "arguments": dict(a, repo=self.root)}) for t, a in calls]):
            if "error" in msg:
                res.append((None, json.dumps(msg["error"])[:200]))
                continue
            text = "".join(c.get("text", "") for c in (msg.get("result") or {}).get("content", [])
                           if isinstance(c, dict)).lstrip()
            try:
                val = json.JSONDecoder().raw_decode(text)[0]
            except ValueError:
                res.append((None, text[:200] or "an empty answer"))
                continue
            if isinstance(val, dict) and "error" in val:
                res.append((None, str(val["error"])[:200]))
            else:
                res.append((val, None))
        return res

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()
            self.p.wait()


def _rows(val):
    """The rows of a struct-column Cypher answer: `[]` when empty, else one JSON object per markdown table row, held to
    the answer's own row_count (a row this parse does not read raises, never drops out)."""
    if isinstance(val, list) and not val:
        return []
    if not isinstance(val, dict):
        raise ValueError("a Cypher answer of an unknown shape: %s" % str(val)[:80])
    rows = [json.loads(ln[2:-2]) for ln in (val.get("markdown") or "").splitlines()[2:]]
    if len(rows) != val.get("row_count"):
        raise ValueError("read %d of %s Cypher rows" % (len(rows), val.get("row_count")))
    return rows


def _gitnexus_meta(root):
    try:
        return json.loads((Path(root) / ".gitnexus" / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _gitnexus(gn, root, rel, sha):
    """(section, [symbol record]) for one file through the shared session `gn` (or a str naming why there is none)."""
    if not reads("gitnexus", rel):
        return {"status": "n/a", "note": "GitNexus does not parse this file type"}, []
    if isinstance(gn, tuple):
        return {"status": gn[0], "note": gn[1]}, []
    meta = _gitnexus_meta(root) or {}
    indexed = (meta.get("fileHashes") or {}).get(rel)
    sec = {"status": "ok", "graph": _fresh(indexed, sha), "indexed_sha256": indexed,
           "indexed_commit": meta.get("lastCommit")}
    try:
        (sv, se), (cv, ce) = gn.tools([("cypher", {"statement": Q_SYMBOLS, "params": {"f": rel}}),
                                       ("cypher", {"statement": Q_CALLERS, "params": {"f": rel}})])
        if se or ce:
            return dict(sec, status="error", note=se or ce), []
        syms, calls = _rows(sv), _rows(cv)
        impacts = gn.tools([("impact", {"target_uid": s["id"], "direction": "upstream", "summaryOnly": True})
                            for s in syms])
    except (OSError, EOFError, TimeoutError, ValueError, KeyError) as e:
        return dict(sec, status="error", note="%s: %s" % (type(e).__name__, e)), []
    callers = {}
    for c in calls:
        name = c.get("name") if c.get("kind") != "File" else "<module>"
        line = c["line"] + 1 if isinstance(c.get("line"), int) else None
        callers.setdefault(c.get("callee"), set()).add((name or "?", c.get("file") or "?", line))
    out = []
    for s, (v, err) in zip(syms, impacts):
        if not isinstance(s.get("s"), int) or not isinstance(s.get("e"), int):
            continue
        rec = {"id": s["id"], "name": s["name"], "kind": (s.get("kind") or "").lower(), "start": s["s"] + 1,
               "end": s["e"] + 1}
        if err:
            rec["risk"], rec["risk_error"] = None, err
        else:
            rec.update(risk=v.get("risk"), impacted=v.get("impactedCount"),
                       direct=(v.get("summary") or {}).get("direct"))
        cs = callers.get(s["id"], set())

        def rank(c, rel=rel):
            return (_is_test(c[1]), c[1] == rel, c[1], c[2] if c[2] is not None else 0, c[0])
        ordered = sorted(cs, key=rank)
        rec["callers"] = {"count": len(cs), "tests": sum(_is_test(c[1]) for c in cs),
                          "sample": [{"name": n, "file": f, "line": ln} for n, f, ln in ordered[:SAMPLE]],
                          "files": sorted({c[1] for c in cs})}
        out.append(rec)
    return sec, out


def _crg(root, rel, sha, env, want_symbols):
    if not reads("code-review-graph", rel):
        return {"status": "n/a", "note": "code-review-graph does not parse this file type"}, [], []
    exe = _which("code-review-graph", env, CRG_FALLBACK)
    if not exe:
        return {"status": "absent", "note": "code-review-graph is not installed"}, [], []
    if not (Path(root) / ".code-review-graph" / "graph.db").is_file():
        return {"status": "no-index", "note": ".code-review-graph/ holds no graph (run `code-review-graph build`)"}, \
            [], []
    indexed = stamp("code-review-graph", root, rel)
    sec = {"status": "ok", "graph": _fresh(indexed, sha), "indexed_sha256": indexed}
    target = os.path.realpath(Path(root) / rel)

    def query(kind):
        r = _run([exe, "query", kind, target], root, env, 120)
        if isinstance(r, str) or r.returncode != 0:
            raise RuntimeError(r if isinstance(r, str) else "rc %d: %s" % (r.returncode, (r.stderr or r.stdout)[-200:]))
        return json.loads(r.stdout)

    try:
        d = query("tests_for")
        tests = sorted({(rel_path(root, x.get("file_path", "")) or x.get("file_path", "?"), x.get("line_start") or 0,
                         x.get("name") or "?", x.get("indirect") is True)
                        for x in d.get("results") or [] if x.get("kind") == "Test" or x.get("is_test")})
        sec["tests_found"] = d.get("result_count", len(tests)) if d.get("status") == "ok" else 0
        if d.get("status") not in ("ok", "not_found"):
            sec["note"] = "tests_for answered %s" % d.get("status")
        syms = []
        if want_symbols:
            for x in query("file_summary").get("results") or []:
                a, b = x.get("line_start"), x.get("line_end")
                if x.get("file_path") == target and x.get("kind") != "File" and type(a) is int and a > 0:
                    syms.append({"name": x.get("name") or "?", "kind": (x.get("kind") or "symbol").lower(),
                                 "start": a, "end": b if type(b) is int and b >= a else a, "signature": ""})
    except (RuntimeError, ValueError) as e:
        return dict(sec, status="error", note=str(e)[:200]), [], []
    return sec, [{"file": f, "line": ln, "name": n, "indirect": ind} for f, ln, n, ind in tests], syms


_AP = {}


def _registry(root, rel, text):
    import contextlib
    import importlib.util
    import io
    try:
        if root not in _AP:
            spec = importlib.util.spec_from_file_location("codemap_ap_screen", Path(root) / "scripts" / "ap_screen.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _AP[root] = (mod, mod._load_screens()[0])
        mod, rows = _AP[root]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            total = mod.screen_texts([(rel, text)], rows, "codemap", limit=10 ** 9)
    except Exception as e:     # the screen's own failure is named, never read as "no rows"
        return {"status": "error", "note": "%s: %s" % (type(e).__name__, str(e)[:160])}, []
    msgs = {r[0]: (r[2] if len(r) > 2 else "") for r in rows}
    hits, row, pre = [], None, "    %s:" % rel
    for ln in buf.getvalue().splitlines():
        m = re.fullmatch(r"(\S+): (\d+)", ln)
        if m:
            row = m.group(1)
        elif row and ln.startswith(pre):
            n, _, t = ln[len(pre):].partition(": ")
            if n.isdigit():
                hits.append({"row": row, "line": int(n), "text": t, "message": " ".join(msgs.get(row, "").split())[:200]})
    if len(hits) != total:   # the screen counts its own hits: a printed line this parse missed is an error, not a pass
        return {"status": "error", "note": "read %d of the screen's %d hits" % (len(hits), total)}, []
    hits.sort(key=lambda h: (h["line"], h["row"]))
    return {"status": "ok", "rows_screened": len(rows)}, hits


# ---------- assembling a pack ----------

def _nest(syms):
    """Qualified names and parents by span containment (graft lists a method or a nested function by its bare name)."""
    out, stack = [], []
    for s in sorted(syms, key=lambda s: (s["start"], -s["end"], s["name"])):
        while stack and not (stack[-1]["start"] <= s["start"] and s["end"] <= stack[-1]["end"]):
            stack.pop()
        s = dict(s, qualname=".".join([p["name"] for p in stack] + [s["name"]]))
        out.append(s)
        stack.append(s)
    return out


def _decorators(text, syms):
    """Python: the first decorator line of each decorated def/class, from the file's own AST (graft and GitNexus spans
    start at the `def`), so an edit on a decorator resolves to the symbol it decorates."""
    import ast
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return
    first = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.decorator_list:
            first[(node.name, node.lineno)] = min(d.lineno for d in node.decorator_list)
    for s in syms:
        if (s["name"], s["start"]) in first:
            s["from"] = first[(s["name"], s["start"])]


def _ast_starts(text):
    """{qualified name: def line} from the file's own AST: the reference a graph's spans are checked against."""
    import ast
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    out = {}

    def walk(node, prefix):
        for n in ast.iter_child_nodes(node):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out.setdefault(prefix + n.name, n.lineno)
                walk(n, prefix + n.name + ".")
            else:
                walk(n, prefix)
    walk(tree, "")
    return out


def _moved(sec, theirs, ours, who):
    """A graph whose own record says it indexed these bytes, but whose symbols start on other lines than the file's:
    its nodes are older than its record (measured 2026-09-25: GitNexus kept the 09-14 spans of
    proofs/S0-08/check_containment.py under a fileHashes entry of the current bytes). Marks the section stale."""
    common = sorted(set(theirs) & set(ours))
    moved = [q for q in common if theirs[q] != ours[q]]
    if moved and sec.get("graph") == "fresh":
        q = moved[0]
        sec.update(graph="stale", note="its record claims these bytes, but %d of %d shared symbols sit on other lines "
                   "in its graph than in the file (first: %s at L%d, the file L%d): %s's nodes are older than its "
                   "record" % (len(moved), len(common), q, theirs[q], ours[q], who))


def _join(syms, gn_recs, fresh):
    """GitNexus data onto the pack's symbols: by (qualified name, start) when both describe the same bytes; by a unique
    qualified name when GitNexus's graph was built from other bytes (lines may have moved)."""
    gn = _nest(gn_recs)
    exact = {(g["qualname"], g["start"]): g for g in gn}
    names = {}
    for g in gn:
        names.setdefault(g["qualname"], []).append(g)
    for s in syms:
        g = exact.get((s["qualname"], s["start"]))
        how = "span"
        if g is None and not fresh and len(names.get(s["qualname"], [])) == 1:
            g, how = names[s["qualname"]][0], "name"
        if g is None:
            s["gitnexus"] = None
            continue
        s["gitnexus"] = {k: g[k] for k in ("id", "risk", "impacted", "direct", "risk_error") if k in g}
        if "callers" in g:
            s["gitnexus"]["callers"] = {k: v for k, v in g["callers"].items() if k != "files"}
        if how == "name":
            s["gitnexus"]["matched_by"] = "name (GitNexus indexed other bytes)"


def _head(root):
    r = _run(["git", "rev-parse", "HEAD"], root, dict(os.environ), 30)
    return r.stdout.strip() if not isinstance(r, str) and r.returncode == 0 else None


def build_one(root, rel, gn, env, commit):
    """Build and write one pack; returns (outcome, pack or None)."""
    import time
    root = Path(root)
    path = root / rel
    if not path.is_file():
        pp = pack_path(root, rel)
        if pp.exists():
            pp.unlink()
            return "removed", None
        return "gone", None
    lang = language(root, rel)
    if not in_scope(rel) or not lang:
        return "skipped", None
    t0 = time.monotonic()
    timing = {"started": round(time.time(), 3)}      # when this build began reading the graphs (the ordering tests)
    data = path.read_bytes()
    text = data.decode("utf-8", "replace")
    sha = hashlib.sha256(data).hexdigest()

    t = time.monotonic()
    graft_sec, syms = _graft(root, rel, sha, env)
    timing["graft_ms"] = round((time.monotonic() - t) * 1000)
    t = time.monotonic()
    crg_sec, tests, crg_syms = _crg(root, rel, sha, env, want_symbols=not syms)
    timing["code_review_graph_ms"] = round((time.monotonic() - t) * 1000)
    source = "graft" if syms else ("code-review-graph" if crg_syms else None)
    syms = _nest(syms or crg_syms)
    starts = _ast_starts(text) if lang == "python" else None
    if lang == "python":
        _decorators(text, syms)
        if starts and source == "graft":
            _moved(graft_sec, {s["qualname"]: s["start"] for s in syms}, starts, "graft")
    t = time.monotonic()
    gn_sec, gn_recs = _gitnexus(gn, root, rel, sha)
    timing["gitnexus_ms"] = round((time.monotonic() - t) * 1000)
    if gn_recs:
        _moved(gn_sec, {g["qualname"]: g["start"] for g in _nest(gn_recs)},
               starts or {s["qualname"]: s["start"] for s in syms}, "GitNexus")
    _join(syms, gn_recs, gn_sec.get("graph") == "fresh")
    caller_files = sorted({f for g in gn_recs for f in g["callers"].get("files", ())} - {rel})
    if gn_sec.get("status") == "ok":
        gn_sec["symbols"] = len(gn_recs)
        gn_sec["unmatched"] = sorted({g["qualname"] for g in _nest(gn_recs)} - {s["qualname"] for s in syms})[:20]
    t = time.monotonic()
    reg_sec, registry = _registry(root, rel, text)
    timing["ap_screen_ms"] = round((time.monotonic() - t) * 1000)
    timing["total_ms"] = round((time.monotonic() - t0) * 1000)
    pack = {"schema": SCHEMA, "path": rel, "language": lang, "blob": blob_sha(data), "sha256": sha,
            "lines": text.count("\n") + (0 if text.endswith("\n") or not text else 1), "bytes": len(data),
            "commit": commit, "symbols_from": source, "caller_files": caller_files,
            "instruments": {"graft": graft_sec, "gitnexus": gn_sec, "code-review-graph": crg_sec, "ap_screen": reg_sec},
            "symbols": syms, "tests": tests, "registry": registry,
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "timing": timing}
    pp = pack_path(root, rel)
    pp.parent.mkdir(parents=True, exist_ok=True)
    tmp = pp.with_name(pp.name + ".%d.tmp" % os.getpid())
    tmp.write_text(json.dumps(pack, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, pp)
    return "built", pack


def open_gitnexus(root, env):
    """A GitNexus session, or (status, why) naming why there is none."""
    exe = _which("gitnexus", env)
    if not exe:
        return ("absent", "gitnexus is not installed (not on PATH)")
    if not (Path(root) / ".gitnexus" / "meta.json").is_file():
        return ("no-index", ".gitnexus/ holds no index (run `gitnexus analyze`)")
    try:
        return GitNexus(exe, root)
    except Exception as e:
        return ("error", "gitnexus mcp did not start: %s: %s" % (type(e).__name__, str(e)[:160]))


def build(root, rels, env=None, gn=None):
    """Build the packs of `rels` (repo-relative) in one pass; one GitNexus session serves every file (`gn`, when the
    caller holds one open, else one opened and closed here)."""
    root = Path(root)
    env = dict(os.environ if env is None else env)
    commit = _head(root)
    own = gn is None and any(in_scope(r) and language(root, r) and reads("gitnexus", r) and (root / r).is_file()
                             for r in rels)
    if own:
        gn = open_gitnexus(root, env)
    results = []
    try:
        for rel in rels:
            results.append((rel,) + build_one(root, rel, gn, env, commit))
    finally:
        if own and isinstance(gn, GitNexus):
            gn.close()
    return results


WIDEN_CAP = 20
Q_CALLEES = ("MATCH (a)-[r:CodeRelation]->(b) WHERE a.filePath = $f AND r.type = 'CALLS' AND b.filePath <> $f "
             "RETURN DISTINCT {file: b.filePath} AS row")


def widen(root, changed, gn):
    """The other code files whose callers this commit may have changed, so their packs are rebuilt too: every in-scope
    file the changed files call into now (GitNexus CALLS edges, from the graph the refresh waited for), and every file
    whose pack names a caller in a changed file (a call this commit removed). Callers further up (the depth-3 risk) are
    not followed. Returns (sorted files, note)."""
    root = Path(root)
    out, notes = set(), []
    if isinstance(gn, GitNexus):
        srcs = [r for r in changed if reads("gitnexus", r) and (root / r).is_file()]
        try:
            for r, (v, err) in zip(srcs, gn.tools([("cypher", {"statement": Q_CALLEES, "params": {"f": r}})
                                                  for r in srcs])):
                if err:
                    notes.append("the callees of %s: %s" % (r, err[:80]))
                else:
                    out |= {x["file"] for x in _rows(v)}
        except (OSError, EOFError, TimeoutError, ValueError, KeyError) as e:
            notes.append("GitNexus callees: %s" % e)
    else:
        notes.append("no callees from GitNexus (%s)" % (gn[0] if isinstance(gn, tuple) else "no session"))
    base = root / PACK_DIR
    ch = set(changed)
    for pp in base.rglob("*.json") if base.is_dir() else ():
        try:
            if ch & set(json.loads(pp.read_text(encoding="utf-8")).get("caller_files") or ()):
                out.add(pp.relative_to(base).as_posix()[:-5])
        except (OSError, ValueError, AttributeError, TypeError):
            continue
    out = sorted(r for r in out - ch if in_scope(r) and language(root, r) and (root / r).is_file())
    if len(out) > WIDEN_CAP:
        notes.append("widening capped at %d of %d files" % (WIDEN_CAP, len(out)))
        out = out[:WIDEN_CAP]
    return out, "; ".join(notes)


def all_code_files(root):
    r = _run(["git", "ls-files", "-z", "--", *[p.rstrip("/") for p in PREFIXES]], root, dict(os.environ), 60)
    if isinstance(r, str) or r.returncode != 0:
        raise SystemExit("codemap: git ls-files failed")
    return [p for p in r.stdout.split("\0") if p and in_scope(p) and language(root, p)]


# ---------- reading a pack ----------

def _cap(text, cap=TEXT_CAP):
    raw = text.encode("utf-8")
    if len(raw) <= cap:
        return text
    tail = " …[cut at %d bytes]" % cap
    return raw[:cap - len(tail.encode("utf-8"))].decode("utf-8", "ignore") + tail


def _where(c):
    return "%s:%s" % (c["file"], c["line"]) if c.get("line") else "%s (module level)" % c["file"]


def _risk_line(s, sec):
    g = s.get("gitnexus")
    if sec.get("status") != "ok":
        return "risk: none — GitNexus %s (%s)" % (sec.get("status"), sec.get("note", ""))
    if g is None:
        return "risk: none — this symbol is not in GitNexus's graph (graph %s)" % sec.get("graph")
    if g.get("risk") is None:
        return "risk: GitNexus impact failed (%s)" % g.get("risk_error", "no answer")
    c = g.get("callers") or {}
    if g["risk"] == "UNKNOWN":
        line = "risk UNKNOWN — " + UNRESOLVED % s["name"]
        if c.get("count"):
            line += " (%d caller%s in its graph, %d in tests)" % (c["count"], "" if c["count"] == 1 else "s",
                                                                    c.get("tests", 0))
        return line
    return "risk %s — GitNexus: %s impacted within 3 hops, %s direct (tests excluded)%s" % (
        g["risk"], g.get("impacted"), g.get("direct"),
        "; from a STALE GitNexus graph, lines may be off" if sec.get("graph") != "fresh" else "")


def _callers_line(s):
    g = s.get("gitnexus")
    if not g or g.get("risk") == "UNKNOWN" and not (g.get("callers") or {}).get("count"):
        return None                                       # UNKNOWN with none found: the risk line says unresolved
    c = g.get("callers") or {}
    if not c.get("count"):
        return "callers: no CALLS edge%s" % ("; the %s direct dependants above are imports or other relations" %
                                              g["direct"] if g.get("direct") else "")
    more = c["count"] - len(c["sample"])
    return "callers %d%s: %s%s" % (c["count"], " (%d in tests)" % c["tests"] if c.get("tests") else "",
                                    " · ".join("%s %s" % (x["name"], _where(x)) for x in c["sample"]),
                                    " · +%d more" % more if more > 0 else "")


def _instruments_line(pack):
    parts = []
    for k in GRAPHS + ("ap_screen",):
        sec = pack["instruments"].get(k) or {}
        st = sec.get("status")
        parts.append("%s %s" % (k, sec.get("graph") if st in ("ok", "no-data") and sec.get("graph") else st))
    return "instruments: " + ", ".join(parts)


def _entry_text(pack, rel, line, end_line, stale, sym, where_rows):
    span = "%d" % line if end_line == line else "%d-%d" % (line, end_line)
    head = "codemap %s:%s — " % (rel, span)
    lines = []
    if sym is None:
        head += "module level (no enclosing symbol; %d symbols in the file)" % len(pack["symbols"])
    else:
        head += "%s %s L%d-%d" % (sym.get("kind", "symbol"), sym["qualname"], sym.get("from", sym["start"]), sym["end"])
        if sym.get("signature"):
            head += " · " + sym["signature"]
    lines.append(head + "  [pack %s]" % pack_path(Path("."), rel).as_posix())
    if stale:
        lines.append("STALE: the file changed since this pack was built (blob %s); lines may have moved" %
                     pack["blob"][:7])
    if sym is not None:
        lines.append(_risk_line(sym, pack["instruments"].get("gitnexus") or {}))
        cl = _callers_line(sym)
        if cl:
            lines.append(cl)
    if where_rows:
        lines.append("registry rows here %d: " % len(where_rows) + " · ".join(
            "%s :%d %s — %s" % (h["row"], h["line"], h["text"][:60], h["message"][:90]) for h in where_rows[:3]))
    t = pack.get("tests") or []
    crg = pack["instruments"].get("code-review-graph") or {}
    if crg.get("status") == "ok":
        lines.append("tests of the file (code-review-graph) %d%s" % (len(t), ": " + " · ".join(
            "%s:%s %s" % (x["file"], x["line"], x["name"]) for x in t[:SAMPLE]) + (" · +%d more" % (len(t) - SAMPLE)
                                                                                   if len(t) > SAMPLE else "")
            if t else " (none found; a test that runs the file as a subprocess leaves no edge)"))
    others = [h for h in pack.get("registry") or [] if h not in where_rows]
    if others:
        lines.append("registry rows elsewhere in the file %d: " % len(others) + ", ".join(
            "%s :%d" % (h["row"], h["line"]) for h in others[:8]) + (" …" if len(others) > 8 else ""))
    lines.append(_instruments_line(pack))
    return _cap("\n".join(lines))


def _load_pack(root, rel):
    p = pack_path(root, rel)
    try:
        pack = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "no pack"
    except (OSError, ValueError) as e:
        return None, "the pack is unreadable (%s)" % type(e).__name__
    if not isinstance(pack, dict) or pack.get("schema") != SCHEMA:
        return None, "the pack has another schema"
    return pack, None


def lookup(path, line, end_line=None, root=None):
    """The entry for the symbol that encloses lines [line, end_line] of `path`, from its pack: a dict with `status`
    (hit, module, past-end, miss, out-of-scope), `stale` (the working file's blob differs from the pack's; None when
    there is no pack) and `text` (at most TEXT_CAP bytes). Reads one pack and hashes the working file: no subprocess."""
    root = Path(root or ROOT)
    rel = rel_path(root, path)
    end_line = line if end_line is None else end_line
    res = {"path": rel or str(path), "line": line, "end_line": end_line, "stale": None, "symbol": None,
           "pack": None if rel is None else pack_path(Path("."), rel).as_posix()}
    if not in_scope(rel) or not language(root, rel):
        return dict(res, status="out-of-scope", pack=None, text="codemap: %s is outside the code map (code files "
                    "under %s)" % (res["path"], ", ".join(PREFIXES)))
    pack, why = _load_pack(root, rel)
    if pack is None:
        return dict(res, status="miss", text="codemap: %s for %s (`python3 scripts/codemap.py build %s` builds "
                    "it)" % (why, rel, rel))
    try:
        stale = blob_sha((root / rel).read_bytes()) != pack["blob"]
    except OSError:
        stale = True
    res["stale"] = stale
    if line < 1 or end_line < line:
        return dict(res, status="miss", text="codemap: line %d-%d is not a line range" % (line, end_line))
    if line > pack["lines"]:
        return dict(res, status="past-end", text="codemap %s:%d — past the end (the pack describes %d lines%s)" % (
            rel, line, pack["lines"], "; STALE: the file changed since" if stale else ""))
    enclosing = [s for s in pack["symbols"] if s.get("from", s["start"]) <= line and end_line <= s["end"]]
    sym = max(enclosing, key=lambda s: (s["start"], -s["end"])) if enclosing else None
    lo, hi = (sym.get("from", sym["start"]), sym["end"]) if sym else (line, end_line)
    if sym is None:     # module level: the rows outside every symbol, in the edited lines first
        inside = [h for h in pack.get("registry") or []
                  if not any(s.get("from", s["start"]) <= h["line"] <= s["end"] for s in pack["symbols"])]
    else:
        inside = [h for h in pack.get("registry") or [] if lo <= h["line"] <= hi]
    res.update(status="hit" if sym else "module", symbol=sym and {k: sym.get(k) for k in (
        "qualname", "kind", "start", "end", "from") if sym.get(k) is not None})
    res["text"] = _entry_text(pack, rel, line, end_line, stale, sym, inside)
    return res


def edit_context(file_path, old_string, root=None, replace_all=False):
    """What L2b injects before an Edit: the line range of `old_string` in the file as it is now (the Edit tool needs it
    unique unless replace_all), the enclosing symbol and its entry. Never guesses a location (D8: the first occurrence
    of the first line named the wrong symbol)."""
    root = Path(root or ROOT)
    rel = rel_path(root, file_path)
    try:
        content = (root / rel).read_bytes().decode("utf-8", "replace") if rel else None
    except OSError:
        content = None
    if content is None or not old_string:
        return {"status": "miss", "path": rel or str(file_path), "ranges": [],
                "text": "codemap: cannot place the edit (%s)" % ("no old_string" if content is not None else
                                                                  "the file is unreadable or outside the repo")}
    ranges, i = [], content.find(old_string)
    while i >= 0:
        a = content.count("\n", 0, i) + 1                      # "\n" only (AF-AP-132)
        ranges.append((a, a + old_string.count("\n", 0, len(old_string) - 1)))
        i = content.find(old_string, i + len(old_string))
    if not ranges:
        return {"status": "miss", "path": rel, "ranges": [], "text": "codemap: old_string is not in %s as it is now "
                "(already applied, or the file changed)" % rel}
    if len(ranges) > 1 and not replace_all:
        return {"status": "ambiguous", "path": rel, "ranges": ranges, "text": "codemap: old_string occurs %d times in "
                "%s (lines %s); the Edit tool refuses a non-unique old_string" % (
                    len(ranges), rel, ", ".join("%d-%d" % r for r in ranges[:5]))}
    res = lookup(rel, ranges[0][0], ranges[0][1], root=root)
    return dict(res, ranges=ranges)


# ---------- the CLI ----------

def _refresh(ns):
    import time
    root = Path(ns.root)
    rels = sorted({r for r in (rel_path(root, p) for p in ns.paths) if r})
    graphs = set(ns.graphs.split())
    waited, secs, notes = wait_for_graphs(root, rels, graphs, Path(ns.lock_dir), ns.wait, ns.grace, ns.poll)
    t = time.monotonic()
    env = dict(os.environ)
    need = [r for r in rels if r.endswith(".py") or in_scope(r)]
    gn = open_gitnexus(root, env) if any(reads("gitnexus", r) and (root / r).is_file() for r in need) else None
    try:
        extra, wnote = widen(root, [r for r in rels if language(root, r)], gn)
        if wnote:
            notes.append(wnote)
        results = build(root, [r for r in rels if in_scope(r)] + extra, env, gn)
    finally:
        if isinstance(gn, GitNexus):
            gn.close()
    counts = {}
    for _, outcome, _ in results:
        counts[outcome] = counts.get(outcome, 0) + 1
    not_fresh = sorted({"%s %s" % (g, pack["instruments"][g].get("graph"))
                        for _, outcome, pack in results if outcome == "built"
                        for g in GRAPHS if pack["instruments"][g].get("graph") not in (None, "fresh")})
    print("%s %s codemap refresh done: %s%s; waited %.0f s for %s%s; build %.1f s%s%s" % (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), (ns.commit or "?")[:7],
        ", ".join("%d %s" % (n, k) for k, n in sorted(counts.items())) or "nothing to do",
        "; widened by %d whose callers changed: %s" % (len(extra), " ".join(extra)) if extra else "",
        secs, " ".join(g for g in GRAPHS if g in graphs) or "no graph",
        "".join("; not ready: %s (%s)" % (g, why) for g, why in sorted(waited.items())),
        time.monotonic() - t, "; graphs not fresh in the packs: " + ", ".join(not_fresh) if not_fresh else "",
        "".join("; " + n for n in notes)), flush=True)
    return 0


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog="codemap.py", description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--all", action="store_true")
    b.add_argument("paths", nargs="*")
    r = sub.add_parser("refresh")
    r.add_argument("--commit", default="")
    r.add_argument("--graphs", default="")
    r.add_argument("--lock-dir", required=True)
    r.add_argument("--wait", type=float, default=1200.0)
    r.add_argument("--grace", type=float, default=30.0)
    r.add_argument("--poll", type=float, default=1.0)
    r.add_argument("paths", nargs="*")
    lk = sub.add_parser("lookup")
    lk.add_argument("path")
    lk.add_argument("--line", type=int, required=True)
    lk.add_argument("--end-line", type=int)
    lk.add_argument("--json", action="store_true")
    d = sub.add_parser("demo")
    d.add_argument("payload")
    d.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    root = Path(ns.root)
    if ns.cmd == "build":
        if not ns.all and not ns.paths:
            ap.error("give PATH... or --all")
        import time
        t = time.monotonic()
        rels = all_code_files(root) if ns.all else [r for r in (rel_path(root, p) for p in ns.paths) if r]
        results = build(root, rels)
        for rel, outcome, pack in results:
            extra = ""
            if pack:
                extra = " %d symbols, %d tests, %d registry rows, %s" % (
                    len(pack["symbols"]), len(pack["tests"]), len(pack["registry"]),
                    ", ".join("%s %s" % (k, v.get("graph") or v.get("status"))
                              for k, v in pack["instruments"].items()))
            print("%s %s%s" % (outcome, rel, extra))
        sizes = [pack_path(root, rel).stat().st_size for rel, outcome, _ in results if outcome == "built"]
        print("codemap build: %d file(s), %d built, %.1f s, %d pack bytes" % (
            len(results), len(sizes), time.monotonic() - t, sum(sizes)))
        return 0
    if ns.cmd == "refresh":
        return _refresh(ns)
    if ns.cmd == "lookup":
        res = lookup(ns.path, ns.line, ns.end_line, root=root)
        print(json.dumps(res, indent=1) if ns.json else res["text"])
        return 0
    raw = sys.stdin.read() if ns.payload == "-" else Path(ns.payload).read_text(encoding="utf-8")
    payload = json.loads(raw)
    ti = payload.get("tool_input", payload) if isinstance(payload, dict) else {}
    if not isinstance(ti, dict) or "file_path" not in ti or "old_string" not in ti:
        print("codemap demo: the payload needs file_path and old_string (an Edit's tool_input)", file=sys.stderr)
        return 2
    res = edit_context(ti["file_path"], ti["old_string"], root=root, replace_all=ti.get("replace_all") is True)
    if ns.json:
        print(json.dumps(res, indent=1))
    else:
        rng = ", ".join("L%d-%d" % r for r in res.get("ranges", [])) or "none"
        sym = res.get("symbol") or {}
        print("old_string at: %s\nenclosing: %s\n--- the entry L2b would inject (%d bytes) ---\n%s" % (
            rng, sym.get("qualname", "module level" if res.get("status") == "module" else res.get("status")),
            len(res["text"].encode("utf-8")), res["text"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
