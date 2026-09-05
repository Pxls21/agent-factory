#!/usr/bin/env python3
"""S0-01 ACP conformance checker — the proof's positive leg, deterministic and LLM-free.

Grades a committed EVIDENCE BUNDLE (raw JSON-RPC frames captured through the byte-preserving tee between
the pinned buzz-acp and the pinned hermes-acp, plus each capture's provenance record) against the six
seed assertions and the golden discipline:

  golden/run-1, golden/run-2   two identical relay-driven prompt turns on the scripted OmniRoute route;
                               their STRUCTURE-PRESERVING normalizations must be byte-identical and
                               equal to the frozen golden/golden.jsonl
  golden/cancel                a turn on the slow scripted model cancelled mid-stream
  golden/shutdown              a clean SIGTERM shutdown after a completed turn
  golden/two-users             two concurrent fixture users, one session each, no cross-talk

Normalization strips volatile VALUES only (JSON-RPC ids and session ids become order-of-appearance
placeholders; text, paths, timestamps, token counts, pids and ports are dropped) and PRESERVES protocol
structure: message-type sequence, event counts, tool-call structure, terminal stop reasons, session
separation. Missing, duplicated, reordered or cross-session events change the normalized text and FAIL.

Exit codes (canonical proof-runner contract): 0 PASS · 1 FAIL (prints `failure_reason: …`) ·
2 DEFERRED — the bundle is absent or incomplete (the route or a leg has not run yet); the runner
records the deferral instead of a fake result.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_initialize as ci  # noqa: E402

PINNED_AGENT_CAPABILITIES = {
    "loadSession": True,
    "promptCapabilities": {"image": True},
    "sessionCapabilities": {"fork": {}, "list": {}, "resume": {}},
}
LEGS = ("run-1", "run-2", "cancel", "shutdown", "two-users")
VOLATILE_UPDATE_FIELDS = {"content", "text", "title", "rawInput", "rawOutput", "locations", "_meta", "usage"}


class Deferred(Exception):
    pass


class Failure(Exception):
    pass


# ----------------------------------------------------------------------------- loading
def load_frames(leg_dir: Path):
    c2a_p, a2c_p = leg_dir / "frames-client-to-agent.jsonl", leg_dir / "frames-agent-to-client.jsonl"
    if not (c2a_p.exists() and a2c_p.exists()):
        raise Deferred(f"{leg_dir.name}: frames absent")
    c2a = [json.loads(l) for l in c2a_p.read_text().splitlines() if l.strip()]
    a2c = [json.loads(l) for l in a2c_p.read_text().splitlines() if l.strip()]
    return c2a, a2c


def load_record(leg_dir: Path) -> dict:
    p = leg_dir / "capture.json"
    if not p.exists():
        raise Deferred(f"{leg_dir.name}: capture.json absent")
    return json.loads(p.read_text())


# ----------------------------------------------------------------------------- normalization
def _shape(value):
    """Structural shadow of a JSON value: types and keys, never scalar content."""
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items()) if k not in VOLATILE_UPDATE_FIELDS}
    if isinstance(value, list):
        return [_shape(v) for v in value]
    if isinstance(value, bool) or value is None:
        return value
    return type(value).__name__


def normalize_run(c2a, a2c):
    """Return the canonical normalized lines for one run (client frames first, then agent frames)."""
    ids, sids = {}, {}

    def id_ph(v):
        key = json.dumps(v, sort_keys=True)
        return ids.setdefault(key, f"<ID{len(ids) + 1}>")

    def sid_ph(v):
        return sids.setdefault(str(v), f"<SID{len(sids) + 1}>")

    out = []
    for o in c2a:
        rec = {"dir": "c2a"}
        if "method" in o and "id" in o:
            params = o.get("params") or {}
            rec.update(kind="req", id=id_ph(o["id"]), method=o["method"])
            if o["method"] == "initialize":
                rec["protocolVersion"] = params.get("protocolVersion")
                rec["clientInfo.name"] = (params.get("clientInfo") or {}).get("name")
                rec["clientCapabilities"] = _shape(params.get("clientCapabilities"))
            elif o["method"] == "session/new":
                rec["mcpServers"] = len(params.get("mcpServers") or [])
            elif o["method"] == "session/prompt":
                rec["sessionId"] = sid_ph(params.get("sessionId"))
                rec["prompt"] = [b.get("type") for b in params.get("prompt") or []]
            else:
                rec["params"] = _shape(params)
        elif "method" in o:
            params = o.get("params") or {}
            rec.update(kind="notif", method=o["method"])
            if "sessionId" in params:
                rec["sessionId"] = sid_ph(params["sessionId"])
        else:
            rec.update(kind="resp", id=id_ph(o.get("id")), result=_shape(o.get("result")), error="error" in o)
        out.append(rec)
    for o in a2c:
        rec = {"dir": "a2c"}
        if "method" in o and "id" not in o:
            params = o.get("params") or {}
            rec.update(kind="notif", method=o["method"], sessionId=sid_ph(params.get("sessionId")))
            upd = params.get("update") if isinstance(params.get("update"), dict) else {}
            rec["sessionUpdate"] = upd.get("sessionUpdate")
            rec["update"] = _shape({k: v for k, v in upd.items() if k not in ("sessionUpdate",)})
        elif "method" in o:
            rec.update(kind="req", id=id_ph(o["id"]), method=o["method"], params=_shape(o.get("params")))
        else:
            res = o.get("result")
            rec.update(kind="resp", id=id_ph(o.get("id")), error="error" in o)
            if isinstance(res, dict):
                rec["result_keys"] = sorted(res)
                if "protocolVersion" in res:
                    rec["protocolVersion"] = res["protocolVersion"]
                    rec["agentCapabilities"] = res.get("agentCapabilities")
                    rec["agentInfo.name"] = (res.get("agentInfo") or {}).get("name")
                if "sessionId" in res:
                    rec["sessionId"] = sid_ph(res["sessionId"])
                if "stopReason" in res:
                    rec["stopReason"] = res["stopReason"]
            else:
                rec["result"] = _shape(res)
        out.append(rec)
    return [json.dumps(r, sort_keys=True, separators=(",", ":")) for r in out]


# ----------------------------------------------------------------------------- assertions
def _responses(a2c):
    return {json.dumps(o["id"], sort_keys=True): o for o in a2c if "id" in o and "method" not in o}


def assert_initialize(c2a, a2c, leg: str):
    """Assertion 1 — the handshake conforms to pinned v1 and carries the pinned capability VALUES."""
    init = [o for o in c2a if o.get("method") == "initialize"]
    if len(init) != 1:
        raise Failure(f"{leg}: expected exactly one initialize request, saw {len(init)}")
    req = init[0]
    resp = _responses(a2c).get(json.dumps(req["id"], sort_keys=True))
    if resp is None or "error" in resp:
        raise Failure(f"{leg}: initialize has no successful response")
    v = ci.classify_request(req["params"])
    if v != "ok":
        raise Failure(f"{leg}: initialize request {v}")
    v = ci.classify_response(resp["result"])
    if v != "ok":
        raise Failure(f"{leg}: initialize response {v}")
    if req["params"].get("protocolVersion") != 2 or resp["result"].get("protocolVersion") != 1:
        raise Failure(f"{leg}: protocol exchange is not client-offered-2/agent-returned-1")
    if resp["result"].get("agentCapabilities") != PINNED_AGENT_CAPABILITIES:
        raise Failure(f"{leg}: agentCapabilities differ from the pinned contract")


def _session_of(o):
    return (o.get("params") or {}).get("sessionId")


def assert_prompt_turn(c2a, a2c, leg: str, expect_stop="end_turn"):
    """Assertion 2 — a prompt turn streams updates and reaches the terminal state."""
    news = [o for o in c2a if o.get("method") == "session/new"]
    prompts = [o for o in c2a if o.get("method") == "session/prompt"]
    if len(news) != 1 or len(prompts) != 1:
        raise Failure(f"{leg}: expected one session/new and one session/prompt, saw {len(news)}/{len(prompts)}")
    resps = _responses(a2c)
    new_resp = resps.get(json.dumps(news[0]["id"], sort_keys=True))
    if not new_resp or "error" in new_resp or not (new_resp.get("result") or {}).get("sessionId"):
        raise Failure(f"{leg}: session/new has no sessionId response")
    sid = new_resp["result"]["sessionId"]
    if _session_of(prompts[0]) != sid:
        raise Failure(f"{leg}: session/prompt targets a different session than session/new returned")
    notifs = [o for o in a2c if "method" in o and "id" not in o]
    kinds = [((o.get("params") or {}).get("update") or {}).get("sessionUpdate") for o in notifs]
    if "agent_message_chunk" not in kinds and expect_stop == "end_turn":
        raise Failure(f"{leg}: no agent_message_chunk streamed before the terminal state")
    bad_sid = {_session_of(o) for o in notifs} - {sid}
    if bad_sid:
        raise Failure(f"{leg}: notifications carry a foreign session id")
    term = resps.get(json.dumps(prompts[0]["id"], sort_keys=True))
    if not term or "error" in term:
        raise Failure(f"{leg}: session/prompt has no successful terminal response")
    stop = (term.get("result") or {}).get("stopReason")
    if stop != expect_stop:
        raise Failure(f"{leg}: terminal stopReason is {stop!r}, expected {expect_stop!r}")
    return sid


def assert_cancel(c2a, a2c, record: dict, leg="cancel"):
    """Assertion 3 — cancellation mid-turn yields the cancelled terminal state and no orphan process."""
    if not any(o.get("method") == "session/cancel" for o in c2a):
        raise Failure(f"{leg}: no session/cancel notification was sent")
    assert_prompt_turn(c2a, a2c, leg, expect_stop="cancelled")
    orphan = record.get("orphan_check") or {}
    if orphan.get("agent_process_alive_after") is not False:
        raise Failure(f"{leg}: capture record does not show the agent process gone after cancel")


def assert_shutdown(record: dict, leg="shutdown"):
    """Assertion 4 — clean shutdown exits 0 with the session closed."""
    sd = record.get("shutdown") or {}
    if sd.get("buzz_acp_exit_code") != 0:
        raise Failure(f"{leg}: buzz-acp exit code is {sd.get('buzz_acp_exit_code')!r}, expected 0")
    if sd.get("agent_process_alive_after") is not False:
        raise Failure(f"{leg}: agent process still alive after shutdown")
    if sd.get("session_completed_before_shutdown") is not True:
        raise Failure(f"{leg}: no completed session before the shutdown")


def assert_two_users(c2a, a2c, leg="two-users"):
    """Assertion 5 — thread-to-session mapping holds with no collision across two concurrent users."""
    news = [o for o in c2a if o.get("method") == "session/new"]
    prompts = [o for o in c2a if o.get("method") == "session/prompt"]
    if len(news) != 2 or len(prompts) != 2:
        raise Failure(f"{leg}: expected two session/new and two session/prompt, saw {len(news)}/{len(prompts)}")
    resps = _responses(a2c)
    sids = []
    for n in news:
        r = resps.get(json.dumps(n["id"], sort_keys=True))
        if not r or "error" in r or not (r.get("result") or {}).get("sessionId"):
            raise Failure(f"{leg}: a session/new lacks a sessionId response")
        sids.append(r["result"]["sessionId"])
    if len(set(sids)) != 2:
        raise Failure(f"{leg}: session ids collide")
    if sorted(_session_of(p) for p in prompts) != sorted(sids):
        raise Failure(f"{leg}: prompts do not map one-to-one onto the two sessions")
    notifs = [o for o in a2c if "method" in o and "id" not in o]
    foreign = {_session_of(o) for o in notifs} - set(sids)
    if foreign:
        raise Failure(f"{leg}: notifications carry a session id belonging to neither user")
    for p in prompts:
        r = resps.get(json.dumps(p["id"], sort_keys=True))
        if not r or (r.get("result") or {}).get("stopReason") != "end_turn":
            raise Failure(f"{leg}: a user's turn did not reach end_turn")
    per_session = Counter(_session_of(o) for o in notifs if ((o.get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk")
    if set(per_session) != set(sids):
        raise Failure(f"{leg}: not every session streamed its own message chunks")


def assert_config_echo(record: dict, leg: str):
    """Assertion 6 — BUZZ_ACP_IDLE_TIMEOUT=900 and the max turn duration are observed (config echo)."""
    echo = record.get("config_echo") or {}
    argv = (record.get("process") or {}).get("argv") or []
    if echo.get("idle_timeout") != "900s" or echo.get("argv_idle_timeout") != "900":
        raise Failure(f"{leg}: idle timeout echo is not 900s")
    if "--idle-timeout" not in argv or argv[argv.index("--idle-timeout") + 1] != "900":
        raise Failure(f"{leg}: argv does not carry --idle-timeout 900")
    if not echo.get("max_turn"):
        raise Failure(f"{leg}: max turn duration not echoed")


def assert_provenance(record: dict, leg: str):
    m = record.get("manifests") or {}
    if not (m.get("identical") is True and m.get("baseline") == m.get("pre_capture") == m.get("post_capture")):
        raise Failure(f"{leg}: source-tree manifests are not identical before/after (or absent)")


# ----------------------------------------------------------------------------- driver
def check_bundle(root: Path) -> str:
    golden = root / "golden"
    if not golden.is_dir():
        raise Deferred("golden evidence bundle absent (the scripted OmniRoute route has not run yet)")
    legs = {}
    for leg in LEGS:
        d = golden / leg
        if not d.is_dir():
            raise Deferred(f"golden/{leg} absent")
        legs[leg] = (*load_frames(d), load_record(d))
    for leg, (c2a, a2c, rec) in legs.items():
        assert_initialize(c2a, a2c, leg)
        assert_provenance(rec, leg)
        assert_config_echo(rec, leg)
    for leg in ("run-1", "run-2"):
        assert_prompt_turn(*legs[leg][:2], leg)
    assert_cancel(*legs["cancel"])
    assert_shutdown(legs["shutdown"][2])
    assert_two_users(*legs["two-users"][:2])
    n1 = normalize_run(*legs["run-1"][:2])
    n2 = normalize_run(*legs["run-2"][:2])
    if n1 != n2:
        first = next((i for i, (a, b) in enumerate(zip(n1, n2)) if a != b), min(len(n1), len(n2)))
        raise Failure(f"golden mismatch between run-1 and run-2 at normalized line {first} (lengths {len(n1)}/{len(n2)})")
    frozen = golden / "golden.jsonl"
    if not frozen.exists():
        raise Deferred("golden/golden.jsonl not frozen yet (write it from a reviewed run-1 normalization)")
    if frozen.read_text().splitlines() != n1:
        raise Failure("normalized runs differ from the frozen golden.jsonl")
    return f"PASS: 6 assertions + golden x2 identical ({len(n1)} normalized lines)"


def main(argv) -> int:
    if len(argv) != 2:
        print("usage: check_acp_conformance.py <evidence-root>", file=sys.stderr)
        return 2
    try:
        print(check_bundle(Path(argv[1])))
        return 0
    except Deferred as d:
        print(f"deferred: {d}")
        return 2
    except Failure as f:
        print(f"failure_reason: {f}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
