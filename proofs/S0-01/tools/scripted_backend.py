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
Every request is recorded to `--record-dir/<seq>.json` (method, path, headers with Authorization
reduced to a fingerprint, parsed body) — raw upstream evidence.
Determinism: identical request bodies -> byte-identical responses (fixed ids, timestamps, usage).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MODELS = ("s0-01-pong", "s0-01-slow")
REPLY = "pong"
SLOW_CHUNKS = ("po", "n", "g", "")  # "" = the final content-less finish chunk
FIXED_CREATED = 1788566400  # 2026-09-05T00:00:00Z, frozen
FIXED_USAGE = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def load_token(path: Path) -> str:
    for line in path.read_text().splitlines():
        if line.startswith("UPSTREAM_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"')
            if token:
                return token
    raise SystemExit(f"scripted_backend: no UPSTREAM_TOKEN= line in {path}")


class State:
    def __init__(self, token: str, record_dir: Path, slow_delay: float):
        self.token = token
        self.record_dir = record_dir
        self.slow_delay = slow_delay
        self.seq = 0
        self.lock = threading.Lock()

    def record(self, method: str, path: str, headers, body) -> int:
        with self.lock:
            self.seq += 1
            n = self.seq
        masked = {}
        for k, v in headers.items():
            masked[k] = f"<bearer fp={_fingerprint(v.split(' ', 1)[-1])}>" if k.lower() == "authorization" else v
        self.record_dir.mkdir(parents=True, exist_ok=True)
        (self.record_dir / f"{n:06d}.json").write_text(json.dumps(
            {"seq": n, "method": method, "path": path, "headers": masked, "body": body}, indent=2, sort_keys=True) + "\n")
        return n


def make_handler(state: State):
    class Handler(BaseHTTPRequestHandler):
        server_version = "s0-01-scripted/1"
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # quiet; the record dir is the log
            return

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
            self._send_json(code, {"error": {"message": message, "type": err_type, "code": err_code}})

        def _authorized(self) -> bool:
            auth = self.headers.get("Authorization", "")
            return auth == f"Bearer {state.token}"

        def _read_body(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            if not raw:
                return None
            return json.loads(raw.decode())

        # -- routes --------------------------------------------------------
        def do_GET(self):
            body = None
            state.record("GET", self.path, self.headers, body)
            if not self._authorized():
                return self._error(401, "missing or invalid upstream bearer", "authentication_error", "unauthorized")
            if self.path.split("?", 1)[0] == "/v1/models":
                return self._send_json(200, {"object": "list", "data": [
                    {"id": m, "object": "model", "created": FIXED_CREATED, "owned_by": "s0-01-scripted"} for m in MODELS]})
            return self._error(404, f"no route {self.path}", "invalid_request_error", "not_found")

        def do_POST(self):
            try:
                body = self._read_body()
            except (ValueError, UnicodeDecodeError):
                state.record("POST", self.path, self.headers, "<invalid json>")
                return self._error(400, "body is not JSON", "invalid_request_error", "bad_request")
            state.record("POST", self.path, self.headers, body)
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
    ap.add_argument("--slow-delay", type=float, default=2.0, help="seconds between s0-01-slow chunks")
    ap.add_argument("--pidfile", type=Path)
    args = ap.parse_args(argv)
    token = load_token(args.token_file)
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
