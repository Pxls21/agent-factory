#!/usr/bin/env python3
"""S0-03 leg A (`direct`) — ONE POST /v1/responses through the REAL OmniRoute, recorded verbatim.

RUNS ON THE PC ONLY. There is no OmniRoute in the sandbox and a sandbox model server is forbidden
(owner ruling 2026-09-03, "just use omniroute"), so nothing here is exercised in the sandbox
beyond its syntax and its argument handling.

Writes `<out-dir>/direct.json`: every streamed event verbatim, the response `model`, `id` and
`usage`, the `X-OmniRoute-Compression` response header, the status and the timing. Recording the
events verbatim is safe by construction — the REQUEST carries no secret in its body, and the
credential lives only in a header this file never writes out (see below).

THE CREDENTIAL (owner ruling 2026-09-05; AF-AP-35, AF-AP-39)
------------------------------------------------------------
Read IN PLACE from the owner's Hermes profile env file, whose path comes from `S0_03_KEY_FILE`
(default `~/.hermes/profiles/agentfactory/.env`, mode 0600). Exactly the `OMNIROUTE_API_KEY=`
line is extracted — that file also carries many unrelated Hermes variables. The value goes
straight into a request header. It is never printed, never placed in argv, never written to any
artifact, and never copied into the repo. This mirrors the technique
`scripts/omniroute_invariants.sh:76-80` uses on the shell side (`curl -H @<fd>`); in Python a
header dict is already argv-free, so no fd dance is needed.
Both failure modes are LOUD, and neither reveals the value:
  * `S0_03_KEY_FILE unreadable`
  * `S0_03_KEY_FILE carries no OMNIROUTE_API_KEY line`

WHY THIS PROBE MUST NOT LOOK LIKE THE CODEX CLI
-----------------------------------------------
OmniRoute rewrites the response `model` field to the CLIENT-REQUESTED id whenever the caller's
`originator` or `user-agent` header starts with "codex"
(`open-sse/handlers/chatCore.ts:1022-1026` via `open-sse/config/codexIdentity.ts:537-538`). Under
that echo the `model` field mirrors the request and asserts nothing about the upstream. This
probe therefore sends an explicit, non-Codex `User-Agent` and no `originator` at all, so the
default upstream-id behaviour (`open-sse/translator/response/openai-responses.ts:199-200`) is the
one under test. The checker does not rely on this holding — conjunct (iii) reads OmniRoute's own
request record — but the leg is built not to poison its own instrument.

Usage: direct_responses_probe.py --route-id ID --out-dir DIR [--base-url URL] [--timeout-s N]
"""
from __future__ import annotations

import datetime
import json
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "http://127.0.0.1:20128/v1"
DEFAULT_KEY_FILE = str(Path.home() / ".hermes" / "profiles" / "agentfactory" / ".env")
DEFAULT_TIMEOUT_S = 120
KEY_NAME = "OMNIROUTE_API_KEY"
KEY_LINE_RE = re.compile(r"^\s*(?:export\s+)?OMNIROUTE_API_KEY\s*=\s*(.*?)\s*$")
# Deliberately NOT "codex*" — see the module docstring.
USER_AGENT = "agent-factory-s0-03/1.0"


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def read_key(key_file: str) -> str:
    """Extract exactly the OMNIROUTE_API_KEY line. Never logs, never returns anything else."""
    path = Path(key_file)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        raise SystemExit(f"direct_responses_probe: S0_03_KEY_FILE unreadable: {key_file}")
    for line in text.splitlines():
        match = KEY_LINE_RE.match(line)
        if match:
            value = match.group(1).strip().strip('"').strip("'")
            if value:
                return value
    raise SystemExit(
        f"direct_responses_probe: S0_03_KEY_FILE carries no {KEY_NAME} line: {key_file}"
    )


def parse_sse(raw: str):
    """Parse an SSE byte stream into the list of parsed `data:` payloads, verbatim and in order.

    Only `data:` lines carry payloads; `event:` lines, comments (`:`) and blanks are separators.
    A payload that is not JSON is preserved as {"_unparsed": "<text>"} rather than dropped — a
    dropped frame is invisible evidence.
    """
    events = []
    for block in raw.split("\n\n"):
        data_lines = [ln[5:].lstrip() for ln in block.splitlines() if ln.startswith("data:")]
        if not data_lines:
            continue
        payload = "\n".join(data_lines).strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            events.append(json.loads(payload))
        except ValueError:
            events.append({"_unparsed": payload})
    return events


def _first_model(events):
    """The response `model` as OmniRoute reports it: the Responses API nests it under
    `response.model` (`open-sse/translator/response/openai-responses.ts:217`); a Chat-Completions
    shaped chunk carries it top-level."""
    for event in events:
        if not isinstance(event, dict):
            continue
        nested = event.get("response")
        if isinstance(nested, dict) and isinstance(nested.get("model"), str):
            return nested["model"]
        if isinstance(event.get("model"), str):
            return event["model"]
    return None


def _first(events, *keys):
    for event in events:
        if not isinstance(event, dict):
            continue
        nested = event.get("response")
        for key in keys:
            if isinstance(nested, dict) and nested.get(key) is not None:
                return nested[key]
            if event.get(key) is not None:
                return event[key]
    return None


def parse_args(argv) -> dict:
    route_id = out_dir = None
    base_url = os.environ.get("S0_03_BASE_URL", DEFAULT_BASE_URL)
    timeout_s = DEFAULT_TIMEOUT_S
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--route-id", "--out-dir", "--base-url", "--timeout-s"):
            if i + 1 >= len(argv):
                raise SystemExit(f"direct_responses_probe: {arg} needs a value")
            value = argv[i + 1]
            if arg == "--route-id":
                route_id = value
            elif arg == "--out-dir":
                out_dir = value
            elif arg == "--base-url":
                base_url = value
            else:
                timeout_s = int(value)
            i += 2
            continue
        raise SystemExit(f"direct_responses_probe: unknown argument {arg}")
    if not route_id or not out_dir:
        raise SystemExit("usage: direct_responses_probe.py --route-id ID --out-dir DIR "
                         "[--base-url URL] [--timeout-s N]")
    return {"route_id": route_id, "out_dir": Path(out_dir), "base_url": base_url.rstrip("/"),
            "timeout_s": timeout_s}


def main(argv) -> int:
    args = parse_args(argv[1:])
    key = read_key(os.environ.get("S0_03_KEY_FILE") or DEFAULT_KEY_FILE)

    nonce = secrets.token_hex(8)
    body = {
        "model": args["route_id"],
        "stream": True,
        "input": [{
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": f"Reply with exactly the token {nonce} and nothing else.",
            }],
        }],
    }
    # The value only ever lives in this dict and in the socket write.
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "User-Agent": USER_AGENT,
        "x-omniroute-compression": "off",
    }
    # What the artifact records: the header NAMES sent, plus the compression value. Never the
    # Authorization value (AF-AP-7: redact structurally, at the point of the write).
    headers_sent = {name: ("<redacted>" if name.lower() == "authorization" else value)
                    for name, value in headers.items()}

    url = f"{args['base_url']}/responses"
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )

    started_at, t0 = _utc(), time.monotonic()
    status, resp_headers, raw, error = None, {}, "", None
    try:
        with urllib.request.urlopen(request, timeout=args["timeout_s"]) as response:
            status = response.status
            resp_headers = {k.lower(): v for k, v in response.headers.items()}
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        resp_headers = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
        raw = exc.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        error = f"{exc.__class__.__name__}: {exc}"
    duration_ms = int((time.monotonic() - t0) * 1000)

    events = parse_sse(raw) if status == 200 else []
    # A non-200 body is NOT an SSE stream (OmniRoute's 401 is a JSON error object); keep it as
    # recorded text so the negative leg's real shape is preserved.
    error_body = None
    if status is not None and status != 200:
        try:
            error_body = json.loads(raw)
        except ValueError:
            error_body = {"_unparsed": raw[:4096]}

    record = {
        "leg": "direct",
        "route_id": args["route_id"],
        "url": url,
        "nonce": nonce,
        "request_headers_sent": headers_sent,
        "request_body": body,
        "status": status,
        "transport_error": error,
        "response_headers": resp_headers,
        "compression_response_header": resp_headers.get("x-omniroute-compression"),
        "model": _first_model(events),
        "id": _first(events, "id"),
        "usage": _first(events, "usage"),
        "events": events,
        "error_body": error_body,
        "started_at": started_at,
        "finished_at": _utc(),
        "duration_ms": duration_ms,
    }
    args["out_dir"].mkdir(parents=True, exist_ok=True)
    (args["out_dir"] / "direct.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"direct: status={status} model={record['model']!r} events={len(events)} "
          f"duration_ms={duration_ms}")
    # A transport error is a FINDING, not a pass: exit non-zero so the runner stops.
    return 0 if status == 200 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
