#!/usr/bin/env python3
"""S0-01 deterministic scripted model backend — the golden's upstream, BEHIND real OmniRoute.

Owner-sanctioned 2026-09-04 ("a deterministic scripted backend behind a dedicated OmniRoute test
route"), needed because two live runs proved the model route's ACP event structure non-reproducible
(proofs/S0-01/evidence/determinism-live-route.json). Everything under test stays REAL — buzz-acp,
hermes-acp, OmniRoute's routing and credential handling; only the model upstream is scripted.
Not S0-03 evidence. Stdlib only; runs on the PC by absolute path.

OpenAI-compatible surface (what OmniRoute's `openai-compatible` provider speaks):
  GET  /v1/models                -> the two scripted models
  POST /v1/chat/completions      -> `s0-01-pong`: reply "pong" (stream or not), never a tool call
                                    `s0-01-slow`: the same reply streamed as 4 chunks with a delay
                                    between them (the cancellation leg needs a turn that is still
                                    running when session/cancel arrives)
Auth: every request must carry `Authorization: Bearer <token>`; the token is read from
`--token-file` (a 0600 file with `UPSTREAM_TOKEN=...`), never from argv. A request without it gets
401 — this proves the call came through OmniRoute carrying the connection's configured credential.
Authorization equality is == (Bearer <token>X -> 401; Bearer <token> extra -> 401).
/healthz matches the exact path only (/healthzXYZ -> 401 + record).

Framing gate (_framing_gate, first statement of do_GET and do_POST):
  1. headers.defects non-empty (parse error, e.g. 'Content-Length : N') -> 400 + close.
  1b. Header value containing CR/LF (obs-fold, RFC 9112 §5.2) -> 400 + close.
  2. Transfer-Encoding present (any value, any count) -> 411 + close.
  3. Duplicate Content-Length -> 400 + close.
  4. Single Content-Length must match [0-9]+ (no sign, underscore, exponent);
     leading OWS in the field value is stripped by the parser
     (Content-Length:  5 -> "5", accepted); trailing OWS is rejected (stricter
     than RFC 9110 §5.5, fail-closed).
     POST with int > MAX_CONTENT_LENGTH -> 400 + close;
     GET with int > 0 -> read min(int, MAX) bytes, 400 + close;
     GET with int == 0 -> accepted.
  5. Expect header present (any value, including empty) -> 417 + close
     (prevents interim 100-continue).
  Unsupported methods (not GET/POST) receive 501 from http.server's
  handle_one_request before dispatch (proven safe: no tail served,
  Connection: close sent).
  Every rejection sends Connection: close and never parses a tail as a second request.

Credential screen (_normal_forms / _carries_secret): breadth-first closure of
  {unquote, unquote_plus, strip_ws, lower, strip_zwc, utf8_redecode} applied to each item,
  deduplicated, bounded at depth 5.  _normal_forms returns (forms, saturated);
  if saturated is False (bound exceeded) the screen fails closed (True) — the
  depth bound affects false-positive breadth, not detection.  strip_zwc removes
  U+200B (ZWSP), U+FEFF (BOM/ZWNBSP), U+00AD (soft hyphen), U+2060 (word joiner).
  Accepted risk (D5d-F12, restored): junk like %25252541 triggers the
  bound-exceeded path and blanks the record (false positive).
  The screen is applied per item (path, header names, header values, serialized
  JSON body, every parsed JSON string — keys AND values — and raw body);
  cross-sink splits are out of contract by design.
  A body the parser cannot decode gets 400 + close.
  F11: records are written with allow_nan=False after coercing non-finite
  floats to the string "<non-finite>". F10: _read_body refuses a JSON nesting
  deeper than MAX_JSON_DEPTH (32) before parsing (400 + close, no record, on
  every interpreter) and _iter_json_strings is iterative to avoid the same.

Not recorded: GET /healthz (operational, pre-auth); any gate rejection (TE, dup CL,
  malformed CL, oversized CL, GET with CL > 0, defects, obs-fold, Expect,
  JSON depth > MAX_JSON_DEPTH, short body). These all close the connection.  Duplicate non-framing headers collapse to the last value in
  the record (email.message.Message.items() yields all, but dict() takes the last --
  documented, not a defect; the dropped duplicate values are discarded and
  unrecoverable from the record).
Determinism: identical request bodies -> byte-identical responses (fixed ids, timestamps, usage).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, unquote_plus

MODELS = ("s0-01-pong", "s0-01-slow")
REPLY = "pong"
SLOW_CHUNKS = ("po", "n", "g", "")  # "" = the final content-less finish chunk
FIXED_CREATED = 1788566400  # 2026-09-05T00:00:00Z, frozen
FIXED_USAGE = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
MAX_CONTENT_LENGTH = 1_048_576
# Deepest JSON nesting a body may carry. CPython's C decoder accepts depth 1000 on 3.12/3.13 (only 3.11 raised
# RecursionError there), so a depth bomb then crashed the handler in the record serializer with NO response
# (CI runs 87-89, 2026-09-06). The gate is a linear scan of the raw bytes, interpreter-independent.
MAX_JSON_DEPTH = 32
# Sentinel object for _read_body control flow (L3: never a bare string — a client
# POSTing the JSON document "BAD_CL" must not collide with the sentinel).
_BAD_CL = object()
# Credential-bearing header names (lowercased) to drop from records (V-c F10).
_CREDENTIAL_HEADERS = frozenset({
    "authorization", "proxy-authorization", "x-api-key", "api-key",
    "x-auth-token", "cookie",
})


class _ParseError(Exception):
    """Raised by _read_body when JSON parsing fails; carries the raw bytes."""
    def __init__(self, raw: bytes):
        self.raw = raw


def _normal_forms(s: str) -> tuple[frozenset[str], bool]:
    """Breadth-first closure of {unquote, unquote_plus, strip_ws, lower, strip_zwc, utf8_redecode}.

    Returns (forms, saturated).  *saturated* is True when the frontier was
    exhausted (all reachable forms found); False when the depth bound (5) was
    exceeded — the caller fails closed on ``not saturated``.

    Accepted risk (D5d-F12, restored): junk like ``%25252541`` triggers the
    bound-exceeded path and blanks the record (false positive).
    """
    strip_ws = lambda x: re.sub(r"\s+", "", x)
    strip_zwc = lambda x: re.sub("[​﻿­⁠]", "", x)
    def utf8_redecode(x):
        """latin-1 re-decode: http.server reads header bytes as latin-1, so
        a UTF-8-encoded separator (e.g. U+200B = e2 80 8b) arrives as three
        latin-1 chars that strip_ws/strip_zwc never touch.  This op recovers
        the real Unicode and the next closure layers strip it."""
        try:
            return x.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return x
    ops = (unquote, unquote_plus, strip_ws, str.lower, strip_zwc, utf8_redecode)
    frontier = {s}
    seen = {s}
    for _depth in range(5):
        new_frontier = set()
        for form in frontier:
            for op in ops:
                v = op(form)
                if v not in seen:
                    seen.add(v)
                    new_frontier.add(v)
        if not new_frontier:
            return frozenset(seen), True      # saturated
        frontier = new_frontier
    return frozenset(seen), False             # bound exceeded — keep what we found


def _json_nesting_depth(raw: bytes) -> int:
    """Maximum bracket nesting of a JSON document, counted on the raw bytes outside strings.

    Runs BEFORE json.loads so the bound does not depend on the interpreter's recursion behaviour.
    A malformed document still gets a number; json.loads decides validity afterwards.
    """
    depth = max_depth = 0
    in_string = escaped = False
    for b in raw:
        if in_string:
            if escaped:
                escaped = False
            elif b == 0x5C:      # backslash
                escaped = True
            elif b == 0x22:      # closing quote
                in_string = False
        elif b == 0x22:
            in_string = True
        elif b in (0x5B, 0x7B):  # [ {
            depth += 1
            if depth > max_depth:
                max_depth = depth
        elif b in (0x5D, 0x7D):  # ] }
            depth -= 1
    return max_depth


def _iter_json_strings(obj):
    """Yield every string leaf (keys and values) from a parsed JSON value.

    F1: json.dumps re-escapes whitespace chars (tab -> \\t, etc.), hiding a
    whitespace-split token.  Walking the parsed values preserves the actual
    whitespace characters that json.loads decoded.
    """
    stack = [obj]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            yield item
        elif isinstance(item, dict):
            for k, v in item.items():
                stack.append(v)
                yield k
        elif isinstance(item, list):
            stack.extend(item)


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def load_token(path: Path) -> str:
    for line in path.read_text().splitlines():
        if line.startswith("UPSTREAM_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"')
            if token:
                return token
    raise SystemExit(f"scripted_backend: no UPSTREAM_TOKEN= line in {path}")


def _validate_slow_delay(s):
    """type= callable for --slow-delay: finite non-negative float (R5-D5-F7)."""
    try:
        v = float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid float: {s!r}")
    if not (math.isfinite(v) and v >= 0):
        print(f"scripted_backend: --slow-delay {v} "
              f"must be a finite number >= 0", file=sys.stderr)
        raise SystemExit(2)
    return v


class State:
    def __init__(self, token: str, record_dir: Path, slow_delay: float):
        self.token = token
        self.record_dir = record_dir
        self.slow_delay = slow_delay
        self.seq = 0
        self.lock = threading.Lock()

    def _carries_secret(self, s: str) -> bool:
        """True if the configured token appears in ANY normal form of *s*,
        or if the closure did not saturate (fail closed).

        Normal forms are the closure of {unquote, unquote_plus, strip_ws,
        lower, strip_zwc, utf8_redecode} over *s*, bounded at depth 5;
        if the bound is exceeded the screen fails closed.
        """
        t = self.token
        forms, saturated = _normal_forms(s)
        if any(t in f for f in forms):
            return True
        return not saturated                  # actually fail closed

    def record(self, method: str, path: str, headers, body,
               remote_addr: str, bearer_token: str | None,
               *, raw_body: bytes | None = None) -> tuple[int, bool]:
        with self.lock:
            self.seq += 1
            n = self.seq
        now = datetime.datetime.now(datetime.timezone.utc)
        received_at = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond:06d}Z"
        mono_ns = time.monotonic_ns()
        # P1/V5/AF-AP-35: credential-leak check at the ONE recording boundary.
        # _carries_secret checks: the closure of {unquote, unquote_plus, strip_ws,
        # lower, strip_zwc, utf8_redecode} at depth 5; fails closed when
        # the bound is exceeded.
        # Keyed on the configured secret, not the request-supplied bearer,
        # so a request without Authorization is still screened (4-F1/6-F3).
        # M12: exempts ONLY 'authorization' by name.
        leaked = False
        if path and self._carries_secret(path):
            leaked = True
        for k, v in headers.items():
            if k.lower() != "authorization":
                if self._carries_secret(str(k)) or self._carries_secret(str(v)):
                    leaked = True
        if body is not None:
            body_str = body if isinstance(body, str) else json.dumps(body)
            if self._carries_secret(body_str):
                leaked = True
            # F1: json.dumps re-escapes whitespace chars to \t \n etc., hiding
            # a whitespace-split token. Walk parsed string values directly.
            if not leaked and not isinstance(body, str):
                for s in _iter_json_strings(body):
                    if self._carries_secret(s):
                        leaked = True
                        break
        if raw_body and self._carries_secret(raw_body.decode("latin-1")):
            leaked = True
        if leaked:
            rec_path = None
            clean = {}
            rec_body = {"credential_in_unexpected_location": True}
            auth_fp = None
        else:
            rec_path = path
            # V-c F3: lowercase keys; V-c F10: drop all credential-bearing headers
            clean = {k.lower(): v for k, v in headers.items()
                     if k.lower() not in _CREDENTIAL_HEADERS}
            rec_body = body
            auth_fp = hashlib.sha256(bearer_token.encode()).hexdigest() if bearer_token else None
        self.record_dir.mkdir(parents=True, exist_ok=True)
        # F11: coerce non-finite floats to the string "<non-finite>" before
        # serialising with allow_nan=False, so the record is always valid JSON.
        # Iterative (F10): no recursion risk regardless of nesting depth.
        def _json_safe(o):
            if isinstance(o, float) and not math.isfinite(o):
                return "<non-finite>"
            if not isinstance(o, (dict, list)):
                return o
            # F12: copy-on-write — never mutates the caller's object.
            root = dict(o) if isinstance(o, dict) else list(o)
            stack = [root]
            while stack:
                item = stack.pop()
                if isinstance(item, dict):
                    for k in list(item):
                        v = item[k]
                        if isinstance(v, float) and not math.isfinite(v):
                            item[k] = "<non-finite>"
                        elif isinstance(v, dict):
                            c = dict(v); item[k] = c; stack.append(c)
                        elif isinstance(v, list):
                            c = list(v); item[k] = c; stack.append(c)
                elif isinstance(item, list):
                    for i in range(len(item)):
                        v = item[i]
                        if isinstance(v, float) and not math.isfinite(v):
                            item[i] = "<non-finite>"
                        elif isinstance(v, dict):
                            c = dict(v); item[i] = c; stack.append(c)
                        elif isinstance(v, list):
                            c = list(v); item[i] = c; stack.append(c)
            return root
        (self.record_dir / f"{n:06d}.json").write_text(json.dumps(
            {"seq": n, "method": method, "path": rec_path, "headers": clean,
             "body": _json_safe(rec_body), "received_at": received_at, "t_mono_ns": mono_ns,
             "remote_addr": remote_addr, "authorization_fingerprint": auth_fp},
            indent=2, sort_keys=True, allow_nan=False) + "\n")
        return n, leaked


def make_handler(state: State):
    class Handler(BaseHTTPRequestHandler):
        server_version = "s0-01-scripted/1"
        protocol_version = "HTTP/1.1"
        timeout = 30  # L4: bound handler threads so an incomplete body cannot block forever

        def log_message(self, fmt, *args):  # quiet; the record dir is the log
            return

        # -- framing gate (allow-list) ----------------------------------------
        def _reject(self, code: int):
            """Send a bare rejection response with Connection: close."""
            self.send_response(code)
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True

        def _framing_gate(self) -> bool:
            """Unified allow-list framing gate.  Returns True if rejected
            (response sent, connection closed).  Called as the FIRST statement
            of do_GET and do_POST."""
            # 1. Header parse defects (e.g. 'Content-Length : N' with space before colon)
            if self.headers.defects:
                self._reject(400)
                return True
            # 1b. Obs-fold (RFC 9112 §5.2): any header value with CR/LF is a
            #     framing defect — a folded CL/TE is invisible to later arms.
            for _k, _v in self.headers.items():
                if '\r' in _v or '\n' in _v:
                    self._reject(400)
                    return True
            # 2. Transfer-Encoding present (any value, any count)
            if self.headers.get_all("Transfer-Encoding"):
                self._reject(411)
                return True
            # 3. Duplicate Content-Length
            cls = self.headers.get_all("Content-Length") or []
            if len(cls) > 1:
                self._reject(400)
                return True
            # 4. Single Content-Length: must be [0-9]+ and within bounds
            if len(cls) == 1:
                cl = cls[0]
                if not re.fullmatch(r"[0-9]+", cl):
                    self._reject(400)
                    return True
                n = int(cl)
                if self.command == "POST":
                    if n > MAX_CONTENT_LENGTH:
                        self._reject(400)
                        return True
                else:  # GET
                    if n > 0:
                        self.rfile.read(min(n, MAX_CONTENT_LENGTH))
                        self._reject(400)
                        return True
            # 5. Expect header present (any value, including empty — F21/F2)
            if self.headers.get_all("Expect") is not None:
                self._reject(417)
                return True
            # Unsupported methods (not GET/POST) receive 501 from http.server's
            # handle_one_request before dispatch (proven safe: no tail served,
            # Connection: close sent). No gate arm needed here.
            return False

        def handle_expect_100(self):
            """Override: suppress 100-continue interim response;
            _framing_gate sends 417 instead."""
            return True  # proceed to do_ method; gate will reject

        # -- helpers -------------------------------------------------------
        def _send_json(self, code: int, obj, extra=None):
            data = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _error(self, code: int, message: str, err_type: str, err_code: str):
            self._send_json(code, {"error": {"message": message, "type": err_type, "code": err_code}},
                            extra={"Connection": "close"})
            self.close_connection = True

        def _authorized(self) -> bool:
            auth = self.headers.get("Authorization", "")
            return auth == f"Bearer {state.token}"

        def _bearer_token(self):
            auth = self.headers.get("Authorization", "")
            return auth[7:] if auth.startswith("Bearer ") else None

        def _read_body(self):
            self._last_raw_body = None
            cl_raw = self.headers.get("Content-Length")
            if cl_raw is None:
                return None
            # Defense-in-depth: gate already validated, but keep for safety
            if not re.fullmatch(r"[0-9]+", cl_raw or ""):
                return _BAD_CL
            length = int(cl_raw)
            if length < 0 or length > MAX_CONTENT_LENGTH:
                return _BAD_CL
            raw = self.rfile.read(length) if length else b""
            # A18: short body (client hung up early) -> _BAD_CL -> 400, no record
            if length and len(raw) < length:
                return _BAD_CL
            self._last_raw_body = raw if raw else None
            if not raw:
                return None
            # F10 (venue-independent): a nesting deeper than MAX_JSON_DEPTH is refused BEFORE parsing —
            # 400 + close, no record — on every interpreter; the RecursionError arm below stays as defence.
            if _json_nesting_depth(raw) > MAX_JSON_DEPTH:
                return _BAD_CL
            try:
                return json.loads(raw.decode())
            except (ValueError, UnicodeDecodeError) as e:
                raise _ParseError(raw) from e

        # -- routes --------------------------------------------------------
        def do_GET(self):
            if self._framing_gate():
                return
            if self.path.split("?", 1)[0] == "/healthz":
                with state.lock:
                    count = state.seq
                return self._send_json(200, {"ok": True, "models": list(MODELS), "records": count})
            bearer = self._bearer_token()
            body = None
            # Record at the single boundary; credential leak handled inside record()
            _seq, leaked = state.record("GET", self.path, self.headers, body,
                                        self.client_address[0], bearer,
                                        raw_body=None)
            if leaked:
                return self._error(400, "credential in unexpected location",
                                   "invalid_request_error", "bad_request")
            if not self._authorized():
                return self._error(401, "missing or invalid upstream bearer", "authentication_error", "unauthorized")
            if self.path.split("?", 1)[0] == "/v1/models":
                return self._send_json(200, {"object": "list", "data": [
                    {"id": m, "object": "model", "created": FIXED_CREATED, "owned_by": "s0-01-scripted"} for m in MODELS]})
            return self._error(404, f"no route {self.path}", "invalid_request_error", "not_found")

        def do_POST(self):
            if self._framing_gate():
                return
            bearer = self._bearer_token()
            try:
                body = self._read_body()
            except _ParseError as e:
                _seq, leaked = state.record(
                    "POST", self.path, self.headers, "<invalid json>",
                    self.client_address[0], bearer, raw_body=e.raw)
                if leaked:
                    return self._error(400, "credential in unexpected location",
                                       "invalid_request_error", "bad_request")
                return self._error(400, "body is not JSON", "invalid_request_error", "bad_request")
            # L3: sentinels are module-level objects compared with `is`
            if body is _BAD_CL:
                self._reject(400)
                return
            # Record at the single boundary; credential leak handled inside record()
            _seq, leaked = state.record("POST", self.path, self.headers, body,
                                        self.client_address[0], bearer,
                                        raw_body=self._last_raw_body)
            if leaked:
                return self._error(400, "credential in unexpected location",
                                   "invalid_request_error", "bad_request")
            if not self._authorized():
                return self._error(401, "missing or invalid upstream bearer", "authentication_error", "unauthorized")
            if self.path.split("?", 1)[0] != "/v1/chat/completions":
                return self._error(404, f"no route {self.path}", "invalid_request_error", "not_found")
            if not isinstance(body, dict) or not isinstance(body.get("messages"), list):
                return self._error(400, "messages: Expected array", "invalid_request_error", "bad_request")
            model = body.get("model")
            if model not in MODELS:
                return self._error(404, f"model {model!r} is not served here", "invalid_request_error", "model_not_found")
            if body.get("stream"):
                return self._stream(model)
            return self._send_json(200, {
                "id": "chatcmpl-s0-01", "object": "chat.completion", "created": FIXED_CREATED, "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": REPLY}, "finish_reason": "stop"}],
                "usage": FIXED_USAGE})

        def _stream(self, model: str):
            chunks = SLOW_CHUNKS if model == "s0-01-slow" else (REPLY, "")
            delay = state.slow_delay if model == "s0-01-slow" else 0.0
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

            def emit(obj):
                self.wfile.write(b"data: " + json.dumps(obj, sort_keys=True, separators=(",", ":")).encode() + b"\n\n")
                self.wfile.flush()

            base = {"id": "chatcmpl-s0-01", "object": "chat.completion.chunk", "created": FIXED_CREATED, "model": model}
            emit({**base, "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}]})
            for i, piece in enumerate(chunks):
                if delay and i:
                    time.sleep(delay)
                if piece == "":
                    emit({**base, "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}], "usage": FIXED_USAGE})
                else:
                    emit({**base, "choices": [{"index": 0, "delta": {"content": piece}, "finish_reason": None}]})
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            self.close_connection = True

    return Handler


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=20201)
    ap.add_argument("--token-file", required=True, type=Path)
    ap.add_argument("--record-dir", required=True, type=Path)
    ap.add_argument("--slow-delay", type=_validate_slow_delay, default=2.0, help="seconds between s0-01-slow chunks")
    ap.add_argument("--pidfile", type=Path)
    ap.add_argument("--allow-existing-records", action="store_true")
    args = ap.parse_args(argv)
    # V17/A18: port range validation
    if not (1 <= args.port <= 65535):
        print(f"scripted_backend: --port {args.port} is outside the valid range 1-65535",
              file=sys.stderr)
        return 2
    # V-d F21: check existence before stat
    if not args.token_file.exists():
        print(f"scripted_backend: token file not found: {args.token_file}",
              file=sys.stderr)
        return 2
    mode = args.token_file.stat().st_mode & 0o7777
    # V-c F15: accept 0600 and 0400 (no group/other bits)
    if mode & 0o077:
        print(f"scripted_backend: token file mode is {oct(mode)}, "
              f"must have no group/other bits (0o600 or 0o400)",
              file=sys.stderr)
        return 2
    token = load_token(args.token_file)
    # V-c F13: refuse when record-dir exists but is not a directory
    if args.record_dir.exists() and not args.record_dir.is_dir():
        print(f"scripted_backend: --record-dir {args.record_dir} exists but is not a directory",
              file=sys.stderr)
        return 2
    if args.record_dir.is_dir() and any(args.record_dir.iterdir()):
        if not args.allow_existing_records:
            print(f"scripted_backend: --record-dir {args.record_dir} is non-empty; "
                  f"pass --allow-existing-records to override", file=sys.stderr)
            return 2
    state = State(token, args.record_dir, args.slow_delay)
    server = ThreadingHTTPServer((args.bind, args.port), make_handler(state))
    if args.pidfile:
        args.pidfile.write_text(f"{os.getpid()}\n")
    print(f"scripted_backend: listening on http://{args.bind}:{server.server_address[1]}/v1 "
          f"models={','.join(MODELS)} record_dir={args.record_dir} token_fp={_fingerprint(token)}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
