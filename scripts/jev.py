#!/usr/bin/env python3
"""jev: a fail-open client for the Laya System One endpoint (task #221 step 1). Advisory only (KC-J1).

Commands (options follow the command):
  health                                     the endpoint's health JSON
  ask      --state T --instructions I [--type noul|choice|score] [--criterion C ...]   one typed question
  rank     --query Q --chunk T [--chunk T ...] [--instructions I]    score each chunk against the query
  classify --state T --label L --label L2 [...] [--instructions I]    one native `choice` question (D-2)
  (--state-file / --query-file / --chunks-file read the text from a file instead)

The wire contract is scripts/laya_systemone_server.py: POST /v1/systemone {"model", "state", "questions": {id: {...}}}.
`rank` sends state = {"query": q, "chunks": [{"id", "text"}, ...]} and one `noul` question per chunk id, so the server
makes one model call per chunk and returns `fan_out` (D-1); a reply without fan_out equal to the chunk count is refused
(the batch form gave every chunk the same score, measured 2026-09-24 12:17Z). The window budget (D-076 b): the query and
each chunk share Laya's 1,024-token window after a head of up to 256 tokens, and the server puts the query first, so
`rank` cuts the query to 1,000 characters and each chunk to 2,500 (after the scrub; a smaller --max-chars still wins),
and it refuses as signal-free a reply whose two or more scores are all equal to 4 decimals (VERIFY-JT1 F-24: a query
of about 3,900 characters cut every chunk out of the window and tied them at 0.4958 with fan_out intact).

Venues (D-3): `--venue auto` (default) tries the local loopback endpoint 127.0.0.1:47411 (its /health must answer
within 1 s), then the PC endpoint through the bridge, then gives up. The PC path reads .pc-bridge.env in-process (the
token is never printed and never in argv), sends the request base64-encoded inside the command, decodes it on the PC,
POSTs it to 127.0.0.1:47411 there with curl, and strips the bridge's `bind: warning: line editing not enabled` text,
which can land on the data line. `--url` pins one loopback endpoint (tests).

Fail-open (D-4): no answer = exit 3 and ONE stderr line `jev: unavailable: <reason>`; a usage error = exit 64. The
import API (`from jev import health, ask, rank, classify`, with scripts/ on sys.path) returns None on any failure and
never raises; `jev.last_reason` holds the reason. Scrub, then cap (D-5, AF-AP-127): every text that leaves the process
(state, query, chunk, instructions, label) passes transcript_export.scrub first, then --max-chars (default 4000; for a
rank's query and chunks, the window budget above when it is smaller).
Call log (D-6): one JSON line per call in .jev/calls.jsonl (dir 0700, file 0600): ts, venue, cmd, n_questions, qtypes,
state_sha256 (of the canonical JSON of the scrubbed, capped state as sent), answers, latency_ms, ok, reason; never the
state text. --no-log skips it. No gate file may import or run this module (scripts/no_laya_in_gates.py). Standard
library only.
"""
import argparse
import base64
import contextlib
import datetime
import hashlib
import http.client
import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from transcript_export import scrub as _scrub
except Exception:          # without the scrubber nothing may leave the process: every call then fails open
    _scrub = None

LOCAL_URL = "http://127.0.0.1:47411"
PC_ENDPOINT = "http://127.0.0.1:47411"      # on the PC, reached through the bridge
HEALTH_PROBE_S = 1.0
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_CHARS = 4000
MAX_CHUNKS = 64
RANK_QUERY_CHARS = 1000     # the window budget (D-076 b): a rank's query, after the scrub
RANK_CHUNK_CHARS = 2500     # ... and each of its chunks
BRIDGE_ENV = os.path.join(ROOT, ".pc-bridge.env")
LOG_DIR = os.path.join(ROOT, ".jev")
LOG_PATH = os.path.join(LOG_DIR, "calls.jsonl")
MODEL = "laya"
RANK_INSTRUCTIONS = "Does this chunk answer, match or explain the query?"
CLASSIFY_INSTRUCTIONS = "Which label fits this text best?"
LOOPBACK = ("127.0.0.1", "localhost", "::1")
_ID = re.compile(r"^[A-Za-z0-9_.:#-]{1,64}$")
# the PC shell's hook prints this on stderr, and the bridge can merge it onto the data line (CLAUDE.md, 2026-09-22).
# Its path starts at `/` and holds only path characters: a `\S*` prefix ate the status digits or the JSON's tail it
# was glued to (this lane's first red run).
_BIND_WARNING = re.compile(r"(?:/[A-Za-z0-9._/-]*bash-hook\.bash: line \d+: )?bind: warning: line editing not enabled")
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # loopback only: never through a proxy

last_reason = None          # the reason of the last failed call (import API)
last_log_error = None       # the reason the last call's log line was not written, if it was not


class Unavailable(Exception):
    """No usable answer from any venue; str() is the reason."""


class Usage(Exception):
    """A caller error: bad arguments, never a call."""


# ---------- request building (scrub, then cap) ----------

def _prep(text, max_chars):
    """Scrub, THEN cap: a cap first can cut a secret below its pattern's minimum length (AF-AP-127)."""
    if _scrub is None:
        raise Unavailable("the scrubber (scripts/transcript_export.py) did not import; nothing is sent")
    return _scrub(str(text))[:max_chars]


def _text(value, what, max_chars):
    if isinstance(value, (dict, list)):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False)
    if not isinstance(value, str):
        raise Usage("%s must be text" % what)
    out = _prep(value, max_chars)
    if not out.strip():
        raise Usage("%s is empty" % what)
    return out


def _check_opts(venue, url, timeout, max_chars):
    if venue not in ("auto", "local", "pc"):
        raise Usage("--venue must be auto, local or pc")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise Usage("--timeout must be a finite number of seconds above 0")
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
        raise Usage("--max-chars must be an integer of at least 1")
    if url is not None:
        u = urllib.parse.urlsplit(url)
        if u.scheme != "http" or u.hostname not in LOOPBACK or u.path not in ("", "/") or u.query or u.fragment:
            raise Usage("--url must be http://<loopback host>[:port] (127.0.0.1, localhost or ::1)")
        try:
            u.port
        except ValueError:
            raise Usage("--url has a bad port")


def _question(qtype, instructions, criteria, max_chars):
    if qtype not in ("noul", "choice", "score"):
        raise Usage("--type must be noul, choice or score")
    q = {"type": qtype, "instructions": _text(instructions, "the instructions", max_chars)}
    if qtype == "noul":
        if criteria:
            raise Usage("a noul question takes no criteria")
        return q
    crit = [_text(c, "a criterion", max_chars) for c in criteria or []]
    if len(crit) < 2 or len(set(crit)) != len(crit):
        raise Usage("a %s question needs at least two distinct criteria (after the scrub and the cap)" % qtype)
    q["criteria"] = crit
    return q


def _build(cmd, args, max_chars):
    """-> (state or None, questions or None, context for the reply check)."""
    if cmd == "health":
        return None, None, {}
    if cmd == "ask":
        state, instructions, qtype, criteria = args
        q = _question(qtype, instructions, criteria, max_chars)
        return _text(state, "the state", max_chars), {"q": q}, {"qtype": qtype, "criteria": q.get("criteria")}
    if cmd == "classify":
        state, labels, instructions = args
        q = _question("choice", instructions, labels, max_chars)
        return _text(state, "the state", max_chars), {"q": q}, {"qtype": "choice", "criteria": q["criteria"]}
    if cmd == "rank":
        query, chunks, instructions = args
        if not isinstance(chunks, (list, tuple)) or not chunks:
            raise Usage("rank needs at least one chunk")
        if len(chunks) > MAX_CHUNKS:
            raise Usage("rank takes at most %d chunks" % MAX_CHUNKS)
        items = []
        for i, c in enumerate(chunks):
            cid, text = ("c%d" % i, c) if isinstance(c, str) else (c.get("id"), c.get("text")) if isinstance(c, dict) else (None, None)
            if not isinstance(cid, str) or not _ID.match(cid) or _prep(cid, 64) != cid:
                raise Usage("chunk id %r must be 1-64 of [A-Za-z0-9_.:#-] and hold nothing the scrubber redacts" % (cid,))
            items.append({"id": cid, "text": _text(text, "chunk %s" % cid,
                                                   min(max_chars, RANK_CHUNK_CHARS))})
        ids = [c["id"] for c in items]
        if len(set(ids)) != len(ids):
            raise Usage("chunk ids must be distinct")
        instr = _text(instructions, "the instructions", max_chars)
        state = {"query": _text(query, "the query", min(max_chars, RANK_QUERY_CHARS)), "chunks": items}
        return state, {cid: {"type": "noul", "instructions": instr} for cid in ids}, {"ids": ids}
    raise Usage("unknown command %r" % cmd)


# ---------- reply checks (a venue whose reply fails its check has not answered) ----------

def _unit(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0.0 <= v <= 1.0


def _check_answer(ans, qtype, criteria):
    if not isinstance(ans, dict) or ans.get("type", qtype) != qtype:
        raise Unavailable("the answer is not a %s answer" % qtype)
    if qtype == "noul":
        if not _unit(ans.get("noul")):
            raise Unavailable("noul is not a finite number in [0, 1]")
        return
    probs = ans.get("probabilities")
    if qtype == "choice":
        if ans.get("choice") not in criteria:
            raise Unavailable("the choice is not one of the labels")
        if not isinstance(probs, dict) or set(probs) != set(criteria) or not all(_unit(v) for v in probs.values()):
            raise Unavailable("the choice probabilities do not cover the labels with numbers in [0, 1]")
    else:
        s = ans.get("score")
        if not (isinstance(s, (int, float)) and not isinstance(s, bool) and math.isfinite(s) and 0 <= s <= len(criteria) - 1):
            raise Unavailable("the score is not a finite number in range")
    if not _unit(ans.get("confidence")):
        raise Unavailable("the confidence is not a finite number in [0, 1]")


def _result(cmd, reply, ctx):
    """Check a venue's reply for `cmd`; return (answers as returned, the command's result fields)."""
    if cmd == "health":
        if reply.get("ok") is not True:
            raise Unavailable("health is not ok")
        return None, {"health": reply}
    answers = reply.get("answers")
    if not isinstance(answers, dict):
        raise Unavailable("the reply has no answers")
    if cmd == "rank":
        ids = ctx["ids"]
        if set(answers) != set(ids):
            raise Unavailable("the reply answers other ids than the chunks")
        if reply.get("fan_out") != len(ids):
            raise Unavailable("no per-chunk fan-out (fan_out=%r for %d chunks)" % (reply.get("fan_out"), len(ids)))
        for cid in ids:
            _check_answer(answers[cid], "noul", None)
        if len(ids) >= 2 and len({round(answers[cid]["noul"], 4) for cid in ids}) == 1:
            # D-076 b (VERIFY-JT1 F-24): one score for every chunk carries no ranking, whatever cut the chunks away
            raise Unavailable("signal-free rank: all %d chunks scored %.4f" % (len(ids), answers[ids[0]]["noul"]))
        order = sorted(range(len(ids)), key=lambda i: (-answers[ids[i]]["noul"], i))
        return answers, {"fan_out": reply["fan_out"], "ranking": [[ids[i], answers[ids[i]]["noul"]] for i in order]}
    if set(answers) != {"q"}:
        raise Unavailable("the reply answers other ids than the question")
    ans = answers["q"]
    _check_answer(ans, ctx["qtype"], ctx["criteria"])
    if cmd == "classify":
        return answers, {"choice": ans["choice"], "confidence": ans["confidence"], "probabilities": ans["probabilities"]}
    return answers, {"answer": ans}


# ---------- venues ----------

def _detail(raw):
    """One scrubbed line (at most 100 characters) of an error body, for the reason."""
    try:
        obj = json.loads(raw)
        msg = obj.get("error") or obj.get("reason") if isinstance(obj, dict) else None
    except ValueError:
        msg = None
    msg = msg if isinstance(msg, str) else (raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw))
    line = " ".join(msg.split())
    return " (%s)" % _scrub(line)[:100] if line and _scrub is not None else ""


def _http(base, path, payload, timeout):
    """The parsed JSON object from a loopback endpoint; Unavailable on refusal, timeout, HTTP error or non-JSON."""
    req = urllib.request.Request(base.rstrip("/") + path, data=payload, method="POST" if payload is not None else "GET",
                                 headers={"Content-Type": "application/json"} if payload is not None else {})
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        raise Unavailable("HTTP %d%s" % (e.code, _detail(body)))
    except urllib.error.URLError as e:
        raise Unavailable(_os_reason(e.reason, timeout))
    except (TimeoutError, OSError) as e:
        raise Unavailable(_os_reason(e, timeout))
    except http.client.HTTPException as e:       # a malformed or cut reply is not an OSError
        raise Unavailable("bad HTTP reply: %s" % type(e).__name__)
    try:
        obj = json.loads(raw)
    except ValueError:
        raise Unavailable("non-JSON reply")
    if not isinstance(obj, dict):
        raise Unavailable("the reply is not a JSON object")
    return obj


def _os_reason(e, timeout):
    if isinstance(e, str):
        return " ".join(e.split())[:80] or "connection failed"
    if isinstance(e, TimeoutError) or "timed out" in str(e):
        return "timeout after %gs" % timeout
    if isinstance(e, ConnectionRefusedError):
        return "connection refused"
    return "%s: %s" % (type(e).__name__, " ".join(str(e).split())[:80])


def _read_bridge_env(path):
    """(url, token) from a KEY=value file; the values never leave this process except to the bridge runner."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        raise Unavailable("no bridge env file")
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
    if not url or not token:
        raise Unavailable("the bridge env file lacks PC_BRIDGE_URL or PC_BRIDGE_TOKEN")
    return url, token


def pc_command(path, payload, timeout):
    """The shell command the bridge runs on the PC: the request travels base64-encoded, curl POSTs it on loopback, and
    the HTTP status follows the body on its own line."""
    t = max(1, int(math.ceil(timeout)))
    tail = "-w '\\n%%{http_code}\\n' %s%s" % (PC_ENDPOINT, path)
    if payload is None:
        return "curl -sS --noproxy '*' -m %d %s" % (t, tail)
    b64 = base64.b64encode(payload).decode("ascii")
    return ("printf %%s '%s' | base64 -d | curl -sS --noproxy '*' -m %d -H 'Content-Type: application/json' "
            "--data-binary @- %s" % (b64, t, tail))


def parse_pc_reply(env):
    """The JSON object from a bridge envelope {rc, stdout, stderr}; `bind: warning` text is stripped wherever it lands."""
    if not isinstance(env, dict):
        raise Unavailable("the bridge envelope is not an object")
    rc = env.get("rc")
    if rc != 0:
        err = " ".join(str(env.get("stderr") or "").split())
        raise Unavailable("remote rc %s%s" % (rc, " (%s)" % _scrub(err)[:80] if err and _scrub is not None else ""))
    out = _BIND_WARNING.sub("", str(env.get("stdout") or ""))
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines or not re.fullmatch(r"\d{3}", lines[-1]):
        raise Unavailable("no HTTP status in the bridge reply")
    status, body = int(lines[-1]), "\n".join(lines[:-1])
    if status != 200:
        raise Unavailable("HTTP %d%s" % (status, _detail(body)))
    try:
        obj = json.loads(body)
    except ValueError:
        raise Unavailable("non-JSON reply")
    if not isinstance(obj, dict):
        raise Unavailable("the reply is not a JSON object")
    return obj


def _pc(path, payload, timeout, bridge_env, runner):
    url, token = _read_bridge_env(bridge_env)
    if runner is None:
        try:
            from pc_bridge_exec import run as runner
        except Exception:
            raise Unavailable("scripts/pc_bridge_exec.py did not import")
    sink = io.StringIO()       # the runner reports on stderr, and curl's text can name the bridge link: never shown
    try:
        with contextlib.redirect_stderr(sink):
            env = runner(pc_command(path, payload, timeout), url, token, attempts=1,
                         max_time=min(110, int(math.ceil(timeout)) + 10))
    except Unavailable:
        raise
    except Exception as e:
        raise Unavailable("bridge runner failed: %s" % type(e).__name__)
    return parse_pc_reply(env)


def _ask_venues(cmd, path, payload, ctx, venue, url, timeout, bridge_env, runner):
    """-> (venue, answers, result fields, latency_ms, server latency_ms); Unavailable naming every venue's reason."""
    order = [("url", url)] if url is not None else [("local", LOCAL_URL)] if venue == "local" else \
        [("pc", None)] if venue == "pc" else [("local", LOCAL_URL), ("pc", None)]
    reasons = []
    for name, base in order:
        try:
            if name == "local" and venue == "auto" and cmd != "health":
                probe = _http(base, "/health", None, HEALTH_PROBE_S)
                if probe.get("ok") is not True:
                    raise Unavailable("health is not ok")
            t = HEALTH_PROBE_S if (name == "local" and venue == "auto" and cmd == "health") else timeout
            t0 = time.monotonic()
            reply = _http(base, path, payload, t) if base is not None else _pc(path, payload, t, bridge_env, runner)
            ms = round((time.monotonic() - t0) * 1000, 1)
            answers, fields = _result(cmd, reply, ctx)
            return name, answers, fields, ms, reply.get("latency_ms")
        except Unavailable as e:
            reasons.append("%s: %s" % (name, e))
    raise Unavailable("; ".join(reasons))


# ---------- the call log ----------

def _write_log(entry, log_path):
    d = os.path.dirname(os.path.abspath(log_path))
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
        os.chmod(d, 0o700)
    elif os.path.abspath(d) == os.path.abspath(LOG_DIR):
        os.chmod(d, 0o700)            # the default dir only: never re-mode a directory the caller named
    fd = os.open(log_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.fchmod(fd, 0o600)
        os.write(fd, (json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    finally:
        os.close(fd)


def _call(cmd, args, venue="auto", url=None, timeout=DEFAULT_TIMEOUT, max_chars=DEFAULT_MAX_CHARS, log=True,
          log_path=None, bridge_env=None, runner=None):
    """One call: build (Usage), ask the venues (Unavailable), log one line, return the result dict."""
    global last_log_error
    _check_opts(venue, url, timeout, max_chars)
    state, questions, ctx = _build(cmd, args, max_chars)
    payload = None if cmd == "health" else json.dumps(
        {"model": MODEL, "state": state, "questions": questions}, ensure_ascii=False).encode("utf-8")
    entry = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "cmd": cmd,
             "n_questions": len(questions or {}), "qtypes": sorted({q["type"] for q in (questions or {}).values()}),
             "state_sha256": None if state is None else hashlib.sha256(json.dumps(
                 state, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest(),
             "venue": None, "answers": None, "latency_ms": None, "ok": False, "reason": None}
    try:
        name, answers, fields, ms, server_ms = _ask_venues(
            cmd, "/health" if cmd == "health" else "/v1/systemone", payload, ctx, venue, url, timeout,
            bridge_env or BRIDGE_ENV, runner)
        entry.update(venue=name, answers=answers, latency_ms=ms, ok=True)
        result = dict(fields, cmd=cmd, venue=name, latency_ms=ms)
        if cmd != "health":
            result["server_latency_ms"] = server_ms
        return result
    except Unavailable as e:
        entry["reason"] = str(e)
        raise
    finally:
        last_log_error = None
        if log:
            try:
                _write_log(entry, log_path or LOG_PATH)
            except Exception as e:
                last_log_error = "%s: %s" % (type(e).__name__, " ".join(str(e).split())[:80])


# ---------- the import API: None on any failure, never an exception (D-4) ----------

def _api(cmd, args, opts):
    global last_reason
    last_reason = None
    try:
        return _call(cmd, args, **opts)
    except Exception as e:
        last_reason = str(e) if isinstance(e, (Unavailable, Usage)) else "internal error: %s" % type(e).__name__
        return None


def health(**opts):
    return _api("health", (), opts)


def ask(state, instructions, qtype="noul", criteria=None, **opts):
    return _api("ask", (state, instructions, qtype, criteria), opts)


def rank(query, chunks, instructions=RANK_INSTRUCTIONS, **opts):
    return _api("rank", (query, chunks, instructions), opts)


def classify(state, labels, instructions=CLASSIFY_INSTRUCTIONS, **opts):
    return _api("classify", (state, labels, instructions), opts)


# ---------- the command line ----------

class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write("jev: usage: %s\n" % message)
        sys.exit(64)


def _read(path, what):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as e:
        raise Usage("cannot read %s file %s: %s" % (what, path, e.strerror))


def main(argv=None):
    common = _Parser(add_help=False)
    common.add_argument("--venue", choices=("auto", "local", "pc"), default="auto")
    common.add_argument("--url", help="pin one loopback endpoint, e.g. http://127.0.0.1:47411 (tests)")
    common.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    common.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    common.add_argument("--no-log", action="store_true")
    common.add_argument("--log-file", help="the call log (default %s)" % LOG_PATH)
    common.add_argument("--bridge-env", help="the bridge env file (default %s)" % BRIDGE_ENV)
    ap = _Parser(prog="jev.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health", parents=[common])
    p = sub.add_parser("ask", parents=[common])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--state")
    g.add_argument("--state-file")
    p.add_argument("--instructions", required=True)
    p.add_argument("--type", default="noul", choices=("noul", "choice", "score"))
    p.add_argument("--criterion", action="append")
    p = sub.add_parser("rank", parents=[common])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--query")
    g.add_argument("--query-file")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--chunk", action="append")
    g.add_argument("--chunks-file", help="a JSON list of texts or of {id, text}")
    p.add_argument("--instructions", default=RANK_INSTRUCTIONS)
    p = sub.add_parser("classify", parents=[common])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--state")
    g.add_argument("--state-file")
    p.add_argument("--label", action="append", required=True)
    p.add_argument("--instructions", default=CLASSIFY_INSTRUCTIONS)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "health":
            args = ()
        elif a.cmd == "ask":
            args = (a.state if a.state is not None else _read(a.state_file, "state"), a.instructions, a.type, a.criterion)
        elif a.cmd == "classify":
            args = (a.state if a.state is not None else _read(a.state_file, "state"), a.label, a.instructions)
        else:
            chunks = a.chunk
            if chunks is None:
                try:
                    chunks = json.loads(_read(a.chunks_file, "chunks"))
                except ValueError:
                    raise Usage("--chunks-file must hold a JSON list")
            args = (a.query if a.query is not None else _read(a.query_file, "query"), chunks, a.instructions)
        result = _call(a.cmd, args, venue=a.venue, url=a.url, timeout=a.timeout, max_chars=a.max_chars,
                       log=not a.no_log, log_path=a.log_file, bridge_env=a.bridge_env)
    except Usage as e:
        sys.stderr.write("jev: usage: %s\n" % e)
        return 64
    except Unavailable as e:
        sys.stderr.write("jev: unavailable: %s\n" % " ".join(str(e).split()))
        return 3
    except Exception as e:     # fail open: one line, no traceback
        sys.stderr.write("jev: unavailable: internal error: %s\n" % type(e).__name__)
        return 3
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    if last_log_error:
        sys.stderr.write("jev: call log not written: %s\n" % last_log_error)
    return 0


if __name__ == "__main__":
    sys.exit(main())
