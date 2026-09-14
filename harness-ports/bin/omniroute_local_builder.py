#!/usr/bin/env python3
"""omniroute_local_builder.py — wire the local Qwen server into OmniRoute as the BUILD lane's first route.

Owner ask 2026-09-14 ("let's get Qwen to do the heavy lifting"). Project rule 3 holds: OmniRoute stays the sole
model egress — Hermes never talks to :8080 directly; this script makes the local server ONE MORE PROVIDER behind
OmniRoute and a combo that tries it first. Everything here is idempotent (ensure twice = create nothing twice) and
runs on the PC with the installed OmniRoute CLI's machine-bound loopback token (harness-ports/bin/omni_api.mjs) —
no password, no owner step. No credential is ever printed: the server key is read from the key FILE that
qwen-server.sh wrote, the inference key (for the consumer-side /v1/models and probe checks) from the Hermes
profile .env, and both leave this process only inside request bodies/headers to loopback.

  omniroute_local_builder.py ensure   node → connection → sync-models → /v1/models lists the model → combo
  omniroute_local_builder.py status   what exists (node id, connection id + test status, combo head, model listed)
  omniroute_local_builder.py probe    one completion through OmniRoute on the COMBO; the served model must be local
  omniroute_local_builder.py remove   delete the combo + connection + node (the local server is untouched)

Contracts (read from the running 3.8.50 instance and the pinned 3.8.51 source, 2026-09-14):
  POST /api/provider-nodes {type:"openai-compatible", name, prefix, apiType:"chat", baseUrl, chatPath, modelsPath,
                            customHeaders:{}}                       → id "openai-compatible-chat-<uuid>"
  POST /api/providers      {provider:<node id>, name, apiKey, priority:1}   (the connection; baseUrl copied from the node)
  POST /api/providers/<connection id>/sync-models
  POST /api/combos         {name, strategy:"priority", enabled:true, models:[{kind:"model", model:"<prefix>/<alias>",
                            providerId:<node id>, weight:0}, …], config:{}, description}
  the exposed model id is "<prefix>/<alias>"; a combo member's prefix resolves to the node (chat.ts #3058 follow-up).
Exit codes: 0 ok · 2 a prerequisite file is missing · 3 the local server is not serving the alias · 4 OmniRoute
refused a call (status + body printed) · 5 the model never appeared in /v1/models · 6 the probe was not served by
the local model · 64 usage.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OMNI_URL = os.environ.get("OMNIROUTE_BASE_URL", "http://127.0.0.1:20128").rstrip("/")
LOCAL_URL = os.environ.get("QWEN_OMNI_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
NODE_NAME = os.environ.get("QWEN_OMNI_NODE", "qwen-local")           # the node name AND the model-id prefix
ALIAS = os.environ.get("QWEN_ALIAS", "qwen3.8-27b-local")             # what llama-server --alias serves
COMBO_NAME = os.environ.get("QWEN_OMNI_COMBO", "agentfactory-build-local")
BASE_COMBO = os.environ.get("QWEN_OMNI_BASE_COMBO", "agentfactory-build")   # its members follow the local model
KEY_FILE = Path(os.environ.get("QWEN_KEY_FILE", Path.home() / ".config" / "qwen-builder" / "api-key"))
INFERENCE_ENV = Path(os.environ.get("OMNIROUTE_INFERENCE_ENV", Path.home() / ".hermes" / "profiles" / "agentfactory" / ".env"))
INFERENCE_KEY_NAME = os.environ.get("OMNIROUTE_INFERENCE_KEY_NAME", "OMNIROUTE_API_KEY")
MODEL_ID = f"{NODE_NAME}/{ALIAS}"


# --- pure payload builders (unit-tested in the sandbox) ------------------------------------------------------
def node_payload(name: str = NODE_NAME, base_url: str = LOCAL_URL) -> dict:
    return {"type": "openai-compatible", "name": name, "prefix": name, "apiType": "chat", "baseUrl": base_url,
            "chatPath": "/v1/chat/completions", "modelsPath": "/v1/models", "customHeaders": {}}


def connection_payload(node_id: str, api_key: str, name: str = NODE_NAME) -> dict:
    return {"provider": node_id, "name": name, "apiKey": api_key, "priority": 1}


def combo_payload(node_id: str, base_combo: dict | None, name: str = COMBO_NAME, model_id: str = MODEL_ID) -> dict:
    """The local model FIRST, then the base combo's members verbatim (their server-assigned ids dropped so the
    server mints fresh ones), priority strategy — the cloud chain stays the fallback when the local server is down."""
    members = [{"kind": "model", "model": model_id, "providerId": node_id, "weight": 0}]
    for m in (base_combo or {}).get("models", []):
        if isinstance(m, str):
            members.append({"kind": "model", "model": m, "weight": 0})
            continue
        entry = {k: v for k, v in m.items() if k != "id"}
        entry.setdefault("weight", 0)
        if entry.get("model") == model_id:
            continue  # never list the local model twice
        members.append(entry)
    return {"name": name, "strategy": "priority", "enabled": True, "models": members, "config": {},
            "description": f"Local {model_id} first (owner 2026-09-14), then the {BASE_COMBO} chain as fallback"}


def env_value(path: Path, key: str) -> str | None:
    """KEY=VALUE lines (optionally `export KEY=VALUE`, quotes stripped); the value is returned, never logged."""
    if not path.is_file():
        return None
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() != key:
            continue
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        return v
    return None


def find_by_name(items: list, name: str) -> dict | None:
    for it in items:
        if isinstance(it, dict) and it.get("name") == name:
            return it
    return None


# --- transports ----------------------------------------------------------------------------------------------
class CliTransport:
    """Management calls through omni_api.mjs (the CLI's machine-bound loopback token)."""

    def __init__(self, node_bin: str = "node", helper: Path = HERE / "omni_api.mjs"):
        self.node_bin, self.helper = node_bin, helper

    def call(self, method: str, path: str, body: dict | None = None):
        env = {k: v for k, v in os.environ.items() if k != "OMNIROUTE_API_KEY"}   # never let an inference key win
        env["OMNIROUTE_BASE_URL"] = OMNI_URL
        tmp = None
        try:
            cmd = [self.node_bin, str(self.helper), method, path]
            if body is not None:
                tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
                json.dump(body, tmp); tmp.close(); cmd.append(tmp.name)
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        finally:
            if tmp is not None:
                os.unlink(tmp.name)
        if r.returncode != 0:
            raise RuntimeError(f"omni_api {method} {path} rc={r.returncode}: {r.stderr.strip()[:300]}")
        status_line, _, text = r.stdout.partition("\n")
        try:
            data = json.loads(text) if text.strip() else None
        except json.JSONDecodeError:
            data = {"_raw": text[:500]}
        return int(status_line.strip()), data


def http_json(url: str, bearer: str | None = None, body: dict | None = None, timeout: float = 30.0):
    req = urllib.request.Request(url, method="POST" if body is not None else "GET")
    if bearer:
        req.add_header("Authorization", f"Bearer {bearer}")
    data = None
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "null")
        except Exception:
            return e.code, None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, {"error": str(e)}


def say(msg: str):
    print(f"omniroute-local-builder: {msg}", flush=True)


def unwrap(data, *keys):
    """OmniRoute wraps lists: {nodes:[…]}, {connections:[…]}, {combos:[…]}."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in keys:
            if isinstance(data.get(k), list):
                return data[k]
    return []


def require(status: int, data, what: str, ok=(200, 201)):
    if status not in ok:
        say(f"{what}: HTTP {status} {json.dumps(data)[:400]}")
        sys.exit(4)
    return data


# --- the operations -------------------------------------------------------------------------------------------
def local_server_serves_alias(server_key: str) -> bool:
    st, data = http_json(f"{LOCAL_URL}/v1/models", bearer=server_key, timeout=10)
    ids = [m.get("id") for m in (data or {}).get("data", [])] if isinstance(data, dict) else []
    return st == 200 and ALIAS in ids


def exposed_model_ids(inference_key: str | None) -> list[str]:
    st, data = http_json(f"{OMNI_URL}/v1/models", bearer=inference_key, timeout=30)
    if st != 200 or not isinstance(data, dict):
        return []
    return [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]


def ensure(t, server_key: str, inference_key: str | None, wait_s: int = 90) -> int:
    if not local_server_serves_alias(server_key):
        say(f"the local server at {LOCAL_URL} does not list {ALIAS} in /v1/models — run qwen-server.sh install first")
        return 3
    nodes = unwrap(require(*t.call("GET", "/api/provider-nodes"), "list nodes"), "nodes")
    node = find_by_name(nodes, NODE_NAME)
    if node is None:
        node = require(*t.call("POST", "/api/provider-nodes", node_payload()), "create node")
        node = node.get("node", node) if isinstance(node, dict) else node
        say(f"node {NODE_NAME} created: {node.get('id')}")
    else:
        say(f"node {NODE_NAME} present: {node.get('id')} (baseUrl {node.get('baseUrl')})")
    node_id = node["id"]
    conns = unwrap(require(*t.call("GET", "/api/providers"), "list connections"), "connections")
    conn = find_by_name(conns, NODE_NAME) or next((c for c in conns if c.get("provider") == node_id), None)
    if conn is None:
        conn = require(*t.call("POST", "/api/providers", connection_payload(node_id, server_key)), "create connection")
        conn = conn.get("connection", conn) if isinstance(conn, dict) else conn
        say(f"connection {NODE_NAME} created: {conn.get('id')}")
    else:
        say(f"connection {NODE_NAME} present: {conn.get('id')} (testStatus {conn.get('testStatus')})")
    # Creating the connection already imports its models (providers/route.ts: a self-fetch of
    # sync-models?mode=import). The explicit sync is called only while the model is still missing — and on the
    # live 3.8.50 it answers 401 to the machine token (2026-09-14), so its status is information, never a gate.
    deadline = time.time() + wait_s
    synced = False
    while True:
        ids = exposed_model_ids(inference_key)
        if MODEL_ID in ids:
            say(f"/v1/models lists {MODEL_ID}")
            break
        if not synced:
            st, data = t.call("POST", f"/api/providers/{conn['id']}/sync-models")
            say(f"sync-models: HTTP {st} {'ok' if st in (200, 201) else json.dumps(data)[:160]}")
            synced = True
        if time.time() > deadline:
            say(f"{MODEL_ID} not in /v1/models after {wait_s}s (saw {len(ids)} ids; the inference key "
                f"{'was' if inference_key else 'was NOT'} available)")
            return 5
        time.sleep(3)
    combos = unwrap(require(*t.call("GET", "/api/combos"), "list combos"), "combos")
    combo = find_by_name(combos, COMBO_NAME)
    if combo is None:
        base = find_by_name(combos, BASE_COMBO)
        if base is None:
            say(f"base combo {BASE_COMBO} not found — the local combo will carry the local model only")
        combo = require(*t.call("POST", "/api/combos", combo_payload(node_id, base)), "create combo")
        combo = combo.get("combo", combo) if isinstance(combo, dict) else combo
        say(f"combo {COMBO_NAME} created: {combo.get('id')} ({len(combo.get('models', []))} members)")
    head = (combo.get("models") or [{}])[0]
    head_model = head.get("model") if isinstance(head, dict) else head
    if head_model != MODEL_ID:
        say(f"combo {COMBO_NAME} exists but its first member is {head_model!r}, not {MODEL_ID} — not rewriting a combo I did not shape")
        return 4
    say(f"combo {COMBO_NAME} head is {MODEL_ID}; {len(combo.get('models', []))} members; strategy {combo.get('strategy')}")
    return 0


def status(t, server_key: str | None, inference_key: str | None) -> int:
    nodes = unwrap(require(*t.call("GET", "/api/provider-nodes"), "list nodes"), "nodes")
    node = find_by_name(nodes, NODE_NAME)
    say(f"node {NODE_NAME}: {node.get('id') if node else 'ABSENT'}")
    conns = unwrap(require(*t.call("GET", "/api/providers"), "list connections"), "connections")
    conn = find_by_name(conns, NODE_NAME)
    say(f"connection {NODE_NAME}: {conn.get('id') if conn else 'ABSENT'}" + (f" testStatus={conn.get('testStatus')} active={conn.get('isActive')}" if conn else ""))
    combos = unwrap(require(*t.call("GET", "/api/combos"), "list combos"), "combos")
    combo = find_by_name(combos, COMBO_NAME)
    if combo:
        chain = [m.get("model") or f"combo:{m.get('comboName')}" if isinstance(m, dict) else m for m in combo.get("models", [])]
        say(f"combo {COMBO_NAME}: {combo.get('id')} enabled={combo.get('enabled')} chain={' -> '.join(chain)}")
    else:
        say(f"combo {COMBO_NAME}: ABSENT")
    say(f"local server serves {ALIAS}: {local_server_serves_alias(server_key) if server_key else 'unknown (no key file)'}")
    ids = exposed_model_ids(inference_key)
    say(f"OmniRoute /v1/models lists {MODEL_ID}: {MODEL_ID in ids} ({len(ids)} ids)")
    return 0 if (node and conn and combo and MODEL_ID in ids) else 1


def probe(inference_key: str | None, model: str = COMBO_NAME) -> int:
    # A nonce per probe: OmniRoute answered an identical repeat in 0.0 s from its response cache (2026-09-14) —
    # a cached pong proves nothing about the server behind the route.
    nonce = os.urandom(4).hex()
    body = {"model": model, "messages": [{"role": "user", "content": f"Reply with the single word pong. (probe {nonce})"}],
            "max_tokens": 256, "temperature": 0}
    t0 = time.time()
    st, data = http_json(f"{OMNI_URL}/v1/chat/completions", bearer=inference_key, body=body, timeout=180)
    if st != 200 or not isinstance(data, dict):
        say(f"probe on {model}: HTTP {st} {json.dumps(data)[:300]}")
        return 4
    served = data.get("model")
    msg = (data.get("choices") or [{}])[0].get("message") or {}
    content = (msg.get("content") or "").strip()
    usage = data.get("usage") or {}
    say(f"probe on {model}: served model={served!r} completion_tokens={usage.get('completion_tokens')} "
        f"reasoning_chars={len(msg.get('reasoning_content') or '')} content={content[:40]!r} wall={time.time() - t0:.1f}s")
    if not served or ALIAS not in str(served):
        say(f"the served model is not the local {ALIAS} — the combo did not route locally")
        return 6
    if "pong" not in content.lower():
        say("no pong in the content")
        return 6
    return 0


def remove(t) -> int:
    combos = unwrap(require(*t.call("GET", "/api/combos"), "list combos"), "combos")
    combo = find_by_name(combos, COMBO_NAME)
    if combo:
        st, d = t.call("DELETE", f"/api/combos/{combo['id']}"); say(f"combo {COMBO_NAME} delete: HTTP {st}")
    conns = unwrap(require(*t.call("GET", "/api/providers"), "list connections"), "connections")
    conn = find_by_name(conns, NODE_NAME)
    if conn:
        st, d = t.call("DELETE", f"/api/providers/{conn['id']}"); say(f"connection {NODE_NAME} delete: HTTP {st}")
    nodes = unwrap(require(*t.call("GET", "/api/provider-nodes"), "list nodes"), "nodes")
    node = find_by_name(nodes, NODE_NAME)
    if node:
        st, d = t.call("DELETE", f"/api/provider-nodes/{node['id']}"); say(f"node {NODE_NAME} delete: HTTP {st}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["ensure", "status", "probe", "remove"])
    ap.add_argument("--wait", type=int, default=90, help="seconds to wait for the model in /v1/models (ensure)")
    ap.add_argument("--model", default=None, help="probe: the model/combo to call (default: the local combo)")
    ns = ap.parse_args(argv)
    t = CliTransport()
    server_key = KEY_FILE.read_text().strip() if KEY_FILE.is_file() else None
    inference_key = env_value(INFERENCE_ENV, INFERENCE_KEY_NAME)
    if ns.cmd == "ensure":
        if not server_key:
            say(f"server key file absent: {KEY_FILE} — run qwen-server.sh install first"); return 2
        return ensure(t, server_key, inference_key, ns.wait)
    if ns.cmd == "status":
        return status(t, server_key, inference_key)
    if ns.cmd == "probe":
        return probe(inference_key, ns.model or COMBO_NAME)
    if ns.cmd == "remove":
        return remove(t)
    return 64


if __name__ == "__main__":
    sys.exit(main())
