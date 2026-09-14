#!/usr/bin/env python3
"""Plumbing proof for harness-ports/bin/omniroute_local_builder.py — the local Qwen server's OmniRoute wiring.

WHAT THIS PROVES: the three payloads match the contracts read from the running OmniRoute (node, connection,
combo — the local model first, the base combo's members copied without their server ids, never twice); the
.env parser returns the value without logging it; `ensure` against a FAKE management API (a labelled test double
of the four endpoints) creates node → connection → combo exactly once and creates nothing on the second run;
it refuses (rc 3) when the local server does not serve the alias, (rc 5) when the model never appears in
/v1/models, (rc 4) when a combo of that name exists with a different head. No network, no OmniRoute, no node.
WHAT IT DOES NOT PROVE: that the real OmniRoute accepts the payloads — that is `ensure` + `probe` on the PC.
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / ".." / "bin" / "omniroute_local_builder.py"
for k in ("QWEN_OMNI_NODE", "QWEN_ALIAS", "QWEN_OMNI_COMBO", "QWEN_OMNI_BASE_COMBO", "QWEN_KEY_FILE",
          "OMNIROUTE_INFERENCE_ENV", "OMNIROUTE_BASE_URL", "QWEN_OMNI_BASE_URL"):
    os.environ.pop(k, None)
spec = importlib.util.spec_from_file_location("olb", SRC)
olb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(olb)

passed = failed = 0


def check(label, cond, why=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"[PASS] {label}")
    else:
        failed += 1
        print(f"[FAIL] {label}  -- {why}")


# --- payloads against the contracts read from the running instance (2026-09-14) -------------------------------
n = olb.node_payload()
check("node payload shape", n == {"type": "openai-compatible", "name": "qwen-local", "prefix": "qwen-local",
                                  "apiType": "chat", "baseUrl": "http://127.0.0.1:8080",
                                  "chatPath": "/v1/chat/completions", "modelsPath": "/v1/models",
                                  "customHeaders": {}}, json.dumps(n))
c = olb.connection_payload("openai-compatible-chat-abc", "sekrit")
check("connection payload shape", c == {"provider": "openai-compatible-chat-abc", "name": "qwen-local",
                                        "apiKey": "sekrit", "priority": 1}, json.dumps(c))
base = {"id": "af-build-v1", "name": "agentfactory-build", "strategy": "priority",
        "models": [{"id": "af-build-sol-ultra", "kind": "model", "model": "codex/gpt-5.6-sol-ultra", "providerId": "codex", "weight": 0},
                   {"id": "af-build-kimi-k3", "kind": "model", "model": "ollama-cloud/kimi-k3", "providerId": "ollama-cloud", "weight": 0},
                   {"id": "af-build-free", "kind": "combo-ref", "comboName": "free-coding", "weight": 0}]}
cp = olb.combo_payload("openai-compatible-chat-abc", base)
check("combo: name/strategy/enabled/config", (cp["name"], cp["strategy"], cp["enabled"], cp["config"]) ==
      ("agentfactory-build-local", "priority", True, {}), json.dumps(cp))
check("combo: the local model is the FIRST member with the node as providerId",
      cp["models"][0] == {"kind": "model", "model": "qwen-local/qwen3.8-27b-local",
                          "providerId": "openai-compatible-chat-abc", "weight": 0}, json.dumps(cp["models"][0]))
check("combo: the base members follow verbatim, server ids dropped, the combo-ref kept",
      cp["models"][1:] == [{"kind": "model", "model": "codex/gpt-5.6-sol-ultra", "providerId": "codex", "weight": 0},
                           {"kind": "model", "model": "ollama-cloud/kimi-k3", "providerId": "ollama-cloud", "weight": 0},
                           {"kind": "combo-ref", "comboName": "free-coding", "weight": 0}], json.dumps(cp["models"][1:]))
check("combo: no member carries an id", all("id" not in m for m in cp["models"]))
twice = olb.combo_payload("nid", {"models": [{"kind": "model", "model": "qwen-local/qwen3.8-27b-local", "weight": 0},
                                              "legacy/string-model"]})
check("combo: the local model is never listed twice; a legacy string member becomes a step",
      [m["model"] for m in twice["models"]] == ["qwen-local/qwen3.8-27b-local", "legacy/string-model"], json.dumps(twice))
check("combo: no base combo → the local model alone", len(olb.combo_payload("nid", None)["models"]) == 1)

# --- the .env parser -----------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as d:
    envf = Path(d) / ".env"
    envf.write_text("# comment\nexport FOO='quoted value'\nOMNIROUTE_API_KEY=\"sk-abc==\"\nBARE=plain\nNOEQ\n")
    check("env: quoted export value", olb.env_value(envf, "FOO") == "quoted value")
    check("env: double-quoted key value", olb.env_value(envf, "OMNIROUTE_API_KEY") == "sk-abc==")
    check("env: bare value", olb.env_value(envf, "BARE") == "plain")
    check("env: missing key → None", olb.env_value(envf, "NOPE") is None)
    check("env: missing file → None", olb.env_value(Path(d) / "absent", "FOO") is None)


# --- a FAKE management API (test double, labelled) ------------------------------------------------------------
class FakeOmni:
    def __init__(self, base_combo=True):
        self.nodes, self.conns, self.combos, self.posts = [], [], [], []
        if base_combo:
            self.combos.append(dict(base))
        self.synced = 0

    def call(self, method, path, body=None):
        if method == "GET" and path == "/api/provider-nodes":
            return 200, {"nodes": list(self.nodes), "total": len(self.nodes)}
        if method == "GET" and path == "/api/providers":
            return 200, {"connections": list(self.conns), "total": len(self.conns)}
        if method == "GET" and path == "/api/combos":
            return 200, {"combos": list(self.combos), "total": len(self.combos)}
        if method == "POST":
            self.posts.append((path, body))
            if path == "/api/provider-nodes":
                node = dict(body, id=f"openai-compatible-chat-{len(self.nodes) + 1:04d}"); self.nodes.append(node); return 201, node
            if path == "/api/providers":
                conn = {k: v for k, v in body.items() if k != "apiKey"}; conn["id"] = f"conn-{len(self.conns) + 1}"
                conn["testStatus"] = "active"; self.conns.append(conn); return 201, conn
            if path.endswith("/sync-models"):
                self.synced += 1; return 200, {"ok": True}
            if path == "/api/combos":
                combo = dict(body, id=f"combo-{len(self.combos) + 1}"); self.combos.append(combo); return 201, combo
        return 404, {"error": path}


# the two HTTP-plane checks are stubbed at the module seam: the local server lists the alias, OmniRoute exposes
# the model once a connection exists (the fake's view of "sync then list")
fake = FakeOmni()
olb.local_server_serves_alias = lambda key: True
olb.exposed_model_ids = lambda key: ["qwen-local/qwen3.8-27b-local"] if fake.conns else ["codex/gpt-5.6-sol-ultra"]
olb.time.sleep = lambda s: None
import io, contextlib
out = io.StringIO()
with contextlib.redirect_stdout(out):
    rc = olb.ensure(fake, "sekrit", "inf-key", wait_s=5)
check("ensure #1 rc 0", rc == 0, out.getvalue())
check("ensure #1 created one node, one connection, one combo", (len(fake.nodes), len(fake.conns), len(fake.combos)) == (1, 1, 2),
      f"{len(fake.nodes)} {len(fake.conns)} {len(fake.combos)}")
check("ensure #1 POSTed node → connection → combo in that order (no sync: the connection's own import listed the model)",
      [p for p, _ in fake.posts] == ["/api/provider-nodes", "/api/providers", "/api/combos"],
      str([p for p, _ in fake.posts]))
check("ensure #1 the connection carries the server key and the node id",
      fake.posts[1][1] == {"provider": "openai-compatible-chat-0001", "name": "qwen-local", "apiKey": "sekrit", "priority": 1})
check("ensure #1 the combo head is the local model on the created node",
      fake.combos[1]["models"][0] == {"kind": "model", "model": "qwen-local/qwen3.8-27b-local",
                                     "providerId": "openai-compatible-chat-0001", "weight": 0})
check("ensure #1 output never carries the server key", "sekrit" not in out.getvalue(), out.getvalue())
posts_before = len(fake.posts)
out2 = io.StringIO()
with contextlib.redirect_stdout(out2):
    rc2 = olb.ensure(fake, "sekrit", "inf-key", wait_s=5)
check("ensure #2 rc 0 and creates NOTHING (idempotent)",
      rc2 == 0 and (len(fake.nodes), len(fake.conns), len(fake.combos)) == (1, 1, 2)
      and fake.posts[posts_before:] == [],
      out2.getvalue() + str(fake.posts[posts_before:]))
check("ensure #2 reports the three as present", all(s in out2.getvalue() for s in ("node qwen-local present", "connection qwen-local present", "combo agentfactory-build-local head is")), out2.getvalue())

# --- the refusals ----------------------------------------------------------------------------------------------
olb.local_server_serves_alias = lambda key: False
with contextlib.redirect_stdout(io.StringIO()):
    rc = olb.ensure(FakeOmni(), "sekrit", "inf-key", wait_s=1)
check("ensure rc 3 when the local server does not serve the alias", rc == 3, str(rc))
olb.local_server_serves_alias = lambda key: True
olb.exposed_model_ids = lambda key: ["codex/gpt-5.6-sol-ultra"]
olb.time.time = (lambda t0=[olb.time.time()]: (lambda: (t0.__setitem__(0, t0[0] + 100) or t0[0])))()
f2 = FakeOmni()
with contextlib.redirect_stdout(io.StringIO()):
    rc = olb.ensure(f2, "sekrit", "inf-key", wait_s=5)
check("ensure rc 5 when the model never appears in /v1/models (node + connection made, ONE sync tried, no combo)",
      rc == 5 and len(f2.combos) == 1 and f2.synced == 1, f"rc={rc} combos={len(f2.combos)} synced={f2.synced}")
olb.exposed_model_ids = lambda key: ["qwen-local/qwen3.8-27b-local"]
f3 = FakeOmni()
f3.combos.append({"id": "x", "name": "agentfactory-build-local", "strategy": "priority",
                  "models": [{"kind": "model", "model": "codex/gpt-5.6-sol-ultra", "weight": 0}]})
with contextlib.redirect_stdout(io.StringIO()):
    rc = olb.ensure(f3, "sekrit", "inf-key", wait_s=5)
check("ensure rc 4 when a same-named combo has a different head (never rewritten)", rc == 4 and len(f3.combos) == 2, str(rc))

print(f"\ntest_omniroute_local_builder: {passed} checks passed" + (f", {failed} FAILED" if failed else ""))
sys.exit(1 if failed else 0)
