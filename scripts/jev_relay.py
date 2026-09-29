#!/usr/bin/env python3
"""jev_relay: the scrubbing relay between the output-pruner plugin and codiv.ai (task #373, D-109; D-078 holds).

The owner (D-109, 2026-09-29): use the codiv key for Jev, and "just build the scrubber". The plugin
`fast-jev-output@fast-jev-output` posts its Jev requests to its `baseUrl` option; pointed at this relay, every request
takes these steps, and a refusal at any step sends nothing upstream:

  1. read at most MAX_BODY bytes and parse them: an object with `state` (a string or an object) and `questions` (an object
     of objects), and optionally `model` (a string; absent means MODEL). Any other top-level key is dropped;
  2. every string in `state` and `questions` passes `transcript_export.scrub_payload` (scrub's named rules, the payload
     rules, the opaque-run rule); an object KEY the scrub would change refuses the request (a question id or a state key
     cannot be rewritten without breaking the answer's mapping);
  3. the value gate: the scrubbed body is checked for the values of the known secrets (transcript_export's
     KNOWN_VALUE_SOURCES, with the key file below among them), whole and by 8-byte windows; a hit refuses;
  4. the model must be one of MODELS;
  5. the body goes to the ONE upstream, `TYPESAFE_BASE_URL` + `/v1/systemone` from the key file, with the key read from
     that file at start (never from argv, never printed). The caller's Authorization header is dropped: the plugin holds
     only a placeholder, so a request that skips the relay is refused upstream;
  6. upstream sends start at least MIN_GAP seconds apart (the API allows 60 requests per minute per key);
  7. the answer goes back with the upstream's status; the key's value, if a reply carries it, is replaced first;
  8. the data log (the owner: fine-tune Laya once there is enough data): one JSON line per relayed request in
     `<state dir>/<UTC day>.jsonl`, and each distinct scrubbed state once in `<state dir>/states/<sha256>.json` (dir 0700,
     files 0600): the scrubbed questions as sent, the answer, the status, the latency and the scrub's sha256. Never a key.

A refusal answers 4xx with one JSON line `{"error": "<reason>"}` that names no value; the plugin then passes the output
through unpruned (its `hook_error` path). Loopback only. Standard library only.

  jev_relay.py serve [--port 47430] [--env-file /root/.codiv/api.env] [--state-dir DIR] [--min-gap 1.05]
                     [--value-file PATH ...] [--no-default-sources] [--no-data]
  GET  /health        -> {ok, pid, upstream_host, models, scrub_sha256, relay_sha256, counts}
  POST /v1/systemone  -> the relayed answer
Exit: 0 stopped cleanly, 2 the key file or a secret source cannot be used, 64 usage, 75 the port is taken.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import transcript_export as te  # noqa: E402  (the scrubber D-078 names, and its value gate)

DEFAULT_ENV_FILE = "/root/.codiv/api.env"
DEFAULT_PORT = 47430
MODEL = "openjev-latest"
MODELS = (MODEL,)
MIN_GAP = 1.05
MAX_BODY = 4 * 1024 * 1024
UPSTREAM_TIMEOUT = 120
USER_AGENT = "python-httpx/0.28.1"          # the header the proven client sends (openjev_j2.py)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main_tree_state_dir():
    """The MAIN tree's .jev/relay, found through the git common dir, as the stack runner finds its log."""
    try:
        common = subprocess.run(["git", "-C", str(HERE), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True, timeout=10).stdout.strip()
        return Path(common).parent / ".jev" / "relay"
    except (OSError, subprocess.SubprocessError):
        return HERE.parent / ".jev" / "relay"


def read_env_file(path):
    """(key, base_url) from the key file. Raises ValueError naming what is missing, never a value."""
    values = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            name = name.strip()
            if name.startswith("export "):
                name = name[len("export "):].strip()
            values[name] = value.strip().strip('"').strip("'")
    key, base = values.get("TYPESAFE_API_KEY", ""), values.get("TYPESAFE_BASE_URL", "")
    if len(key) < 8:
        raise ValueError("TYPESAFE_API_KEY is missing or short in %s" % path)
    parts = urllib.parse.urlsplit(base)
    if parts.scheme not in ("https", "http") or not parts.hostname:
        raise ValueError("TYPESAFE_BASE_URL is missing or not a URL in %s" % path)
    return key, base.rstrip("/")


class Refused(Exception):
    """args[0] is the HTTP status, args[1] the reason (never a value)."""


def scrub_tree(value, where="body"):
    """The value with every string scrubbed; an object key the scrub would change raises Refused."""
    if isinstance(value, str):
        return te.scrub_payload(value)
    if isinstance(value, list):
        return [scrub_tree(v, where) for v in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if te.scrub_payload(k) != k:
                raise Refused(422, "an object key in %s holds a secret shape" % where)
            out[k] = scrub_tree(v, where)
        return out
    return value


def parse_request(raw):
    """-> the body to send (model, state, questions), scrubbed. Raises Refused."""
    try:
        body = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise Refused(400, "the body is not JSON")
    if not isinstance(body, dict):
        raise Refused(400, "the body is not a JSON object")
    state, questions, model = body.get("state"), body.get("questions"), body.get("model", MODEL)
    if not isinstance(state, (str, dict)):
        raise Refused(400, "state must be a string or an object")
    if not isinstance(questions, dict) or not questions or not all(isinstance(q, dict) for q in questions.values()):
        raise Refused(400, "questions must be a non-empty object of objects")
    if model not in MODELS:
        raise Refused(400, "the model is not one this relay sends to (%s)" % ", ".join(MODELS))
    return {"model": model, "state": scrub_tree(state, "state"), "questions": scrub_tree(questions, "questions")}


class Relay:
    def __init__(self, key, base, values, state_dir, min_gap, data):
        self.key, self.url = key, base + "/v1/systemone"
        self.key_bytes = key.encode()
        self.values = values
        self.state_dir = Path(state_dir) if data else None
        self.min_gap = min_gap
        self.lock = threading.Lock()
        self.last_send = 0.0
        self.counts = {"requests": 0, "relayed": 0, "refused": 0, "upstream_error": 0}
        self.scrub_sha = sha256_file(Path(te.__file__))
        self.relay_sha = sha256_file(__file__)
        no_proxy = urllib.parse.urlsplit(base).hostname in ("127.0.0.1", "localhost")
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}) if no_proxy
                                                  else urllib.request.ProxyHandler())

    def count(self, name):
        with self.lock:
            self.counts[name] += 1

    def health(self):
        with self.lock:
            counts = dict(self.counts)
        return {"ok": True, "pid": os.getpid(), "upstream_host": urllib.parse.urlsplit(self.url).hostname,
                "models": list(MODELS),
                "scrub_sha256": self.scrub_sha, "relay_sha256": self.relay_sha, "counts": counts}

    def clean_reply(self, data):
        """The upstream's reply with the key's value replaced (an error body that echoes it)."""
        return data.replace(self.key_bytes, b"<redacted>")

    def wait_turn(self):
        with self.lock:
            now = time.monotonic()
            start = max(now, self.last_send + self.min_gap)
            self.last_send = start
        if start > now:
            time.sleep(start - now)

    def handle(self, raw):
        """-> (status, reply bytes)."""
        self.count("requests")
        try:
            body = parse_request(raw)
            sent = json.dumps(body, ensure_ascii=False, sort_keys=True).encode()
            hits = te.value_hits([sent], self.values)
            if hits:
                raise Refused(422, "the value gate found %d known secret form(s) in the scrubbed body" % len(hits))
        except Refused as e:
            self.count("refused")
            return e.args[0], json.dumps({"error": e.args[1]}).encode()
        self.wait_turn()
        started = time.monotonic()
        req = urllib.request.Request(self.url, data=sent, method="POST", headers={
            "Content-Type": "application/json", "User-Agent": USER_AGENT, "Authorization": "Bearer " + self.key})
        try:
            with self.opener.open(req, timeout=UPSTREAM_TIMEOUT) as r:
                status, reply = r.status, r.read(MAX_BODY)
        except urllib.error.HTTPError as e:
            status, reply = e.code, e.read(MAX_BODY)
        except (urllib.error.URLError, OSError) as e:
            self.count("upstream_error")
            return 502, json.dumps({"error": "the upstream is unreachable (%s)" % type(e).__name__}).encode()
        reply = self.clean_reply(reply)
        self.count("relayed" if status == 200 else "upstream_error")
        self.log(body, sent, status, reply, int((time.monotonic() - started) * 1000))
        return status, reply

    def log(self, body, sent, status, reply, latency_ms):
        if self.state_dir is None:
            return
        try:
            answer = json.loads(reply)
        except ValueError:
            answer = None
        state_bytes = json.dumps(body["state"], ensure_ascii=False, sort_keys=True).encode()
        state_sha = hashlib.sha256(state_bytes).hexdigest()
        row = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
               "model": body["model"], "state_sha256": state_sha, "body_sha256": hashlib.sha256(sent).hexdigest(),
               "questions": body["questions"], "status": status, "answer": answer, "latency_ms": latency_ms,
               "scrub_sha256": self.scrub_sha, "relay_sha256": self.relay_sha}
        line = (json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode()
        if te.value_hits([line, state_bytes], self.values):      # the answer is upstream text: it is checked too
            print("jev_relay: the data log refused a row (a known value); nothing written", file=sys.stderr)
            return
        with self.lock:
            states = self.state_dir / "states"
            states.mkdir(mode=0o700, parents=True, exist_ok=True)
            os.chmod(self.state_dir, 0o700)
            sp = states / (state_sha + ".json")
            if not sp.exists():
                fd = os.open(sp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as fh:
                    fh.write(state_bytes)
            day = self.state_dir / (row["ts"][:10] + ".jsonl")
            fd = os.open(day, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            with os.fdopen(fd, "ab") as fh:
                fh.write(line)


def make_handler(relay):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, data):
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self._send(200, json.dumps(relay.health()).encode())
            else:
                self._send(404, b'{"error": "not found"}')

        def do_POST(self):
            if self.path not in ("/v1/systemone", "/v1/classifier"):
                self._send(404, b'{"error": "not found"}')
                return
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                self._send(411, b'{"error": "a Content-Length is required"}')
                return
            if length < 0 or length > MAX_BODY:
                relay.count("requests")
                relay.count("refused")
                self._send(413, json.dumps({"error": "the body is over %d bytes" % MAX_BODY}).encode())
                return
            status, reply = relay.handle(self.rfile.read(length))
            self._send(status, reply)

        def log_message(self, fmt, *args):      # no request lines on stderr: a path or a status is all it would add
            return
    return Handler


def serve(args):
    try:
        key, base = read_env_file(args.env_file)
    except (OSError, ValueError) as e:
        print("jev_relay: the key file cannot be used: %s" % (e if isinstance(e, ValueError) else type(e).__name__),
              file=sys.stderr)
        return 2
    defaults = () if args.no_default_sources else tuple(s for s in te.KNOWN_VALUE_SOURCES if s[1] != DEFAULT_ENV_FILE)
    sources = defaults + (("env-file", args.env_file, ("TYPESAFE_BASE_URL",)),) + tuple(
        ("env-file", p, ()) for p in args.value_file)
    try:
        values = te.known_values(sources)
    except te.KnownValueRefusal as e:
        print("jev_relay: " + "; ".join(e.args[0]), file=sys.stderr)
        return 2
    relay = Relay(key, base, values, args.state_dir or main_tree_state_dir(), args.min_gap, not args.no_data)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(relay))
    except OSError as e:
        print("jev_relay: port %d cannot be bound (%s); is a relay already running?" % (args.port, type(e).__name__),
              file=sys.stderr)
        return 75
    print("jev_relay: serving 127.0.0.1:%d -> %s (%d known secret forms)" % (
        args.port, urllib.parse.urlsplit(base).hostname, len(values)), file=sys.stderr, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jev_relay.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=DEFAULT_PORT)
    s.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    s.add_argument("--state-dir", default=None)
    s.add_argument("--min-gap", type=float, default=MIN_GAP)
    s.add_argument("--value-file", action="append", default=[], help="an extra env file whose values the gate knows")
    s.add_argument("--no-default-sources", action="store_true", help="tests: know only --env-file and --value-file")
    s.add_argument("--no-data", action="store_true", help="keep no data log")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 64 if e.code else 0
    if not 0 < args.port < 65536 or not math.isfinite(args.min_gap) or args.min_gap < 0:   # NaN passes a bare < 0
        print("jev_relay: bad --port or --min-gap", file=sys.stderr)
        return 64
    return serve(args)


if __name__ == "__main__":
    sys.exit(main())
