#!/usr/bin/env python3
"""One-shot GitNexus MCP client over **stdio** — the tier-2 fallback when the native MCP integration is
disconnected but the server itself is fine (which is the common failure mode here).

It speaks JSON-RPC 2.0 to `node .gitnexus/run.cjs mcp`: initialize -> initialized -> tools/call, then prints
the tool's text result. Same capabilities as the native MCP tools, no live session integration needed.

Usage:
  python scripts/gn_mcp.py --list
  python scripts/gn_mcp.py impact         '{"target":"rerank","direction":"upstream"}'
  python scripts/gn_mcp.py detect_changes '{"scope":"compare","base_ref":"main"}'
  python scripts/gn_mcp.py context        '{"name":"recall"}'

Preference order (see CLAUDE.md): native MCP tools first; this stdio client when they are down; the
`node .gitnexus/run.cjs <subcommand>` CLI as the last resort.
"""
import json
import os
import select
import subprocess
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _drive(requests, want_id=2, timeout=120):
    """Drive the stdio MCP server and return {id: message}. CRITICAL: a tool call runs an async graph query,
    so stdin must stay OPEN until the response arrives — closing it early (as subprocess.run does) makes the
    server treat EOF as a disconnect and shut down before answering. We Popen, write the batch, keep stdin
    open, and read with a select() timeout until the wanted response surfaces."""
    proc = subprocess.Popen(["node", ".gitnexus/run.cjs", "mcp"], cwd=_ROOT,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for r in requests:
        proc.stdin.write(json.dumps(r) + "\n")
    proc.stdin.flush()                                   # but DO NOT close stdin yet
    out = {}
    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            ready, _, _ = select.select([proc.stdout], [], [], min(1.0, deadline - time.time()))
            if not ready:
                continue
            line = proc.stdout.readline()
            if not line:                                 # server closed stdout
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
    return out, (proc.stderr.read() if proc.stderr else "")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    base = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "gn_mcp", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]
    if args[0] == "--list":
        base.append({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    else:
        tool = args[0]
        try:
            targs = json.loads(args[1]) if len(args) > 1 else {}
        except json.JSONDecodeError as e:
            print(f"bad JSON args: {e}", file=sys.stderr)
            return 2
        base.append({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                     "params": {"name": tool, "arguments": targs}})

    responses, stderr = _drive(base)
    msg = responses.get(2)
    if msg is None:
        print("no response from gitnexus mcp\n" + stderr[-800:], file=sys.stderr)
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
