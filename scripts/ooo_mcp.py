#!/usr/bin/env python3
"""One-shot Ouroboros MCP client over **stdio** — the tier-2 fallback when the native MCP integration is
disconnected but the `ouroboros` binary is fine (the common failure mode here).

Speaks JSON-RPC 2.0 to `ouroboros mcp serve`: initialize -> initialized -> tools/call, prints the text
result. The interview is server-side STATEFUL and persists to ~/.ouroboros/data/interview_*.json, so a
multi-round interview is driven by repeated calls keyed on session_id (resume with session_id, NOT
interview_id). Keeps stdin OPEN across the async call (closing it early makes the server treat EOF as a
disconnect and exit before answering).

Usage:
  python scripts/ooo_mcp.py --list
  python scripts/ooo_mcp.py ouroboros_interview '{"initial_context":"...", "ambiguity_score":1.0}'   # NOT goal/topic (verified 2026-08-22)
  python scripts/ooo_mcp.py ouroboros_interview '{"session_id":"...", "last_question":"...", "answer":"...", "ambiguity_score":0.2}'
"""
import json
import os
import select
import subprocess
import sys
import time

# 2026-09-01: the installed ouroboros tool env can no longer host `mcp serve`
# (MCP-SDK v2 vs the [claude-sdk] extra's v1.x — profile split upstream). The
# native command stays first; on its failure signature the driver retries via
# an ISOLATED uvx env with the [mcp] profile and the claude-cli runtime.
_SERVE = ["ouroboros", "mcp", "serve"]
_SERVE_ISOLATED = ["uvx", "--prerelease", "allow", "--isolated", "--python", ">=3.12",
                   "--from", "ouroboros-ai[mcp]", "ouroboros", "mcp", "serve",
                   "--runtime", "claude-cli"]
# IS_SANDBOX=1 is REQUIRED for any call that drives the nested claude backend (interview,
# auto, seed generation): ouroboros runs it with --dangerously-skip-permissions, which the
# CLI refuses as root unless IS_SANDBOX is set (see sandbox-kit/OUROBOROS-SETUP.md §2a).
# Interview rounds can exceed 3 min (nested LLM call), hence the 600s default.
_ENV = {**os.environ, "IS_SANDBOX": "1"}


def _drive(requests, want_id=2, timeout=600, serve_cmd=None):
    if serve_cmd is None:
        serve_cmd = _SERVE
    proc = subprocess.Popen(serve_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, env=_ENV)
    for r in requests:
        proc.stdin.write(json.dumps(r) + "\n")
    proc.stdin.flush()                                   # keep stdin OPEN
    out = {}
    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            ready, _, _ = select.select([proc.stdout], [], [], min(1.0, deadline - time.time()))
            if not ready:
                continue
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "id" in msg:
                out[msg["id"]] = msg
                if msg["id"] == want_id:
                    break
    finally:
        try:
            proc.stdin.close()
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    return out, (proc.stderr.buffer.read().decode("utf-8", errors="replace") if proc.stderr else "")  # raw-bytes read: a truncated multibyte char in ouroboros stderr crashed the text-mode read (2026-08-01)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    base = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "ooo_mcp", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]
    if args[0] == "--list":
        base.append({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    else:
        targs = json.loads(args[1]) if len(args) > 1 else {}
        base.append({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                     "params": {"name": args[0], "arguments": targs}})
    responses, stderr = _drive(base)
    # Auto-fallback (2026-09-01): the native env prints an MCP-SDK/profile
    # complaint and answers nothing -- retry once via the isolated uvx env.
    if not responses and ("MCP dependencies not installed" in stderr
                          or "Unsupported package profiles" in stderr):
        print("native serve unavailable -- retrying via isolated uvx env", file=sys.stderr)
        responses, stderr = _drive(base, serve_cmd=_SERVE_ISOLATED)
    msg = responses.get(2)
    if msg is None:
        print("no response from ouroboros mcp\n" + stderr[-1000:], file=sys.stderr)
        return 1
    if "error" in msg:
        print("MCP error:", json.dumps(msg["error"]), file=sys.stderr)
        return 1
    result = msg.get("result", {})
    if args[0] == "--list":
        for t in result.get("tools", []):
            print(f"{t['name']}\t{(t.get('description') or '').splitlines()[0][:90]}")
    else:
        for chunk in result.get("content", []):
            if chunk.get("type") == "text":
                print(chunk["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
