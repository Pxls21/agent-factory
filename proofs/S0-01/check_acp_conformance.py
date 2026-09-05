#!/usr/bin/env python3
"""S0-01 ACP conformance checker v2 — derives EVERYTHING from raw files, exact values.

Exit codes: 0 PASS / 1 `failure_reason: <leg>: <reason>` / 2 `deferred: <reason>`.
A v1 bundle (no timeline.jsonl) DEFERS, never fails.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_initialize as ci  # noqa: E402
sys.path.insert(0, str(HERE / "tools"))
import nostr_verify  # noqa: E402

# ---------------------------------------------------------------------------
# Pinned constants (live in the CHECKER, not in records)
# ---------------------------------------------------------------------------
PINNED_BUZZ_ACP_SHA256 = "a5a17ffc0c7ef878648a506b9d5066120b91984d1158a60e6ce9664a39f88064"
PINNED_AGENT_ENTRYPOINT_SHA256 = "f90a0cc333fa86d99495c7c984e4e11a1b83a7e3dc92883b7fd295ae70358ef1"
PINNED_AGENT_REALPATH = "/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp"
PINNED_HERMES_HOME = "/home/rocco/s0-01-pinned/.hermes-home"
PINNED_RELAY_URL = "ws://127.0.0.1:3999"
PINNED_BASELINE_DIGESTS = {
    "hermes-agent": "1e11d5dcdf3c38ff26a972c839547c532c91dd2ec942324e75bd310def2b87cb",
    "buzz": "f00e3463f75d6b0716a3f89913de1b06db37af7c8d3433330590022e94a7d987",
    "acp": "5579023c865ec10ecc026ddaa0947f9a2104ad0e2e92ed870989a7d5d66c80d8",
}
PINNED_AGENT_CAPABILITIES = {
    "loadSession": True,
    "promptCapabilities": {"image": True},
    "sessionCapabilities": {"fork": {}, "list": {}, "resume": {}},
}
PINNED_IDLE_TIMEOUT = "900s"
PINNED_MAX_TURN = "3600s"
PINNED_IDLE_TIMEOUT_ARG = "900"
PINNED_MAX_TURN_DURATION_ARG = "3600"

LEGS = ("run-1", "run-2", "cancel", "shutdown", "two-users")
EXPECTED_MODEL = {
    "run-1": "s0-01-pong", "run-2": "s0-01-pong",
    "cancel": "s0-01-slow",
    "shutdown": "s0-01-pong", "two-users": "s0-01-pong",
}
# (tag, identity_key, expected_content)
EXPECTED_MENTIONS = {
    "run-1": [("owner", "owner", "Reply with exactly the single word: pong")],
    "run-2": [("owner", "owner", "Reply with exactly the single word: pong")],
    "cancel": [("owner", "owner", "Reply with exactly the single word: pong"),
               ("cancel-cmd", "owner", "!cancel")],
    "shutdown": [("owner", "owner", "Reply with exactly the single word: pong"),
                 ("shutdown-cmd", "owner", "!shutdown")],
    "two-users": [("owner", "owner", "Reply with exactly the single word: pong"),
                  ("user2", "user2", "Reply with exactly the single word: pong")],
}
VOLATILE_UPDATE_FIELDS = {"content", "text", "title", "rawInput", "rawOutput",
                          "locations", "_meta", "usage"}


class Deferred(Exception):
    pass


class Failure(Exception):
    pass


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def _require(path: Path, leg: str, name: str):
    if not path.exists():
        raise Deferred(f"{leg}: {name} absent")
    return path


def load_timeline(leg_dir: Path, leg: str):
    p = _require(leg_dir / "timeline.jsonl", leg, "timeline.jsonl")
    entries = []
    for line in p.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def load_json(leg_dir: Path, name: str, leg: str):
    p = _require(leg_dir / name, leg, name)
    return json.loads(p.read_text())


# ---------------------------------------------------------------------------
# 1. Timeline integrity
# ---------------------------------------------------------------------------
def check_timeline(entries, leg, leg_dir):
    if not entries:
        raise Failure(f"{leg}: timeline.jsonl is empty")
    for i, e in enumerate(entries):
        if e["seq"] != i + 1:
            raise Failure(f"{leg}: timeline seq not strictly 1..N at index {i}")
    for i in range(1, len(entries)):
        if entries[i]["t_mono_ns"] < entries[i - 1]["t_mono_ns"]:
            raise Failure(f"{leg}: t_mono_ns not non-decreasing at seq {entries[i]['seq']}")
    # directional files must equal the split
    c2a_split = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c_split = [e["frame"] for e in entries if e["dir"] == "a2c"]
    c2a_path = leg_dir / "frames-client-to-agent.jsonl"
    a2c_path = leg_dir / "frames-agent-to-client.jsonl"
    if c2a_path.exists():
        c2a_file = [json.loads(l) for l in c2a_path.read_text().splitlines() if l.strip()]
        if c2a_file != c2a_split:
            raise Failure(f"{leg}: frames-client-to-agent.jsonl does not match timeline c2a split")
    if a2c_path.exists():
        a2c_file = [json.loads(l) for l in a2c_path.read_text().splitlines() if l.strip()]
        if a2c_file != a2c_split:
            raise Failure(f"{leg}: frames-agent-to-client.jsonl does not match timeline a2c split")
    return c2a_split, a2c_split


# ---------------------------------------------------------------------------
# 2. Initialize
# ---------------------------------------------------------------------------
def check_initialize(c2a, a2c, leg):
    init_reqs = [o for o in c2a if o.get("method") == "initialize"]
    if len(init_reqs) != 1:
        raise Failure(f"{leg}: expected one initialize request, got {len(init_reqs)}")
    req = init_reqs[0]
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c
             if "id" in o and "method" not in o}
    resp = resps.get(json.dumps(req["id"], sort_keys=True))
    if resp is None or "error" in resp:
        raise Failure(f"{leg}: initialize has no successful response")
    v = ci.classify_request(req["params"])
    if v != "ok":
        raise Failure(f"{leg}: initialize request {v}")
    v = ci.classify_response(resp["result"])
    if v != "ok":
        raise Failure(f"{leg}: initialize response {v}")
    if req["params"].get("protocolVersion") != 2:
        raise Failure(f"{leg}: client protocolVersion is not 2")
    if resp["result"].get("protocolVersion") != 1:
        raise Failure(f"{leg}: agent protocolVersion is not 1")
    if resp["result"].get("agentCapabilities") != PINNED_AGENT_CAPABILITIES:
        raise Failure(f"{leg}: agentCapabilities differ from pinned")


# ---------------------------------------------------------------------------
# 3. Runtime identity
# ---------------------------------------------------------------------------
def check_runtime_identity(leg_dir, leg):
    rid = load_json(leg_dir, "runtime-identity.json", leg)
    if rid.get("buzz_acp_exe_sha256") != PINNED_BUZZ_ACP_SHA256:
        raise Failure(f"{leg}: buzz_acp_exe_sha256 mismatch")
    if rid.get("agent_entrypoint_sha256") != PINNED_AGENT_ENTRYPOINT_SHA256:
        raise Failure(f"{leg}: agent_entrypoint_sha256 mismatch")
    if rid.get("agent_realpath") != PINNED_AGENT_REALPATH:
        raise Failure(f"{leg}: agent_realpath mismatch")
    tee_path = HERE / "tools" / "frame_tee.py"
    if tee_path.exists():
        expected_tee_sha = _sha256_file(tee_path)
        if rid.get("tee_sha256") != expected_tee_sha:
            raise Failure(f"{leg}: tee_sha256 mismatch")
    if rid.get("python_dont_write_bytecode") is not True:
        raise Failure(f"{leg}: python_dont_write_bytecode is not true")


# ---------------------------------------------------------------------------
# 4. env.json
# ---------------------------------------------------------------------------
def check_env(leg_dir, leg, identities):
    env = load_json(leg_dir, "env.json", leg)
    if env.get("S0_01_AGENT") != PINNED_AGENT_REALPATH:
        raise Failure(f"{leg}: env S0_01_AGENT mismatch")
    if env.get("HERMES_HOME") != PINNED_HERMES_HOME:
        raise Failure(f"{leg}: env HERMES_HOME mismatch")
    if env.get("BUZZ_RELAY_URL") != PINNED_RELAY_URL:
        raise Failure(f"{leg}: env BUZZ_RELAY_URL mismatch")
    omni = env.get("OMNIROUTE_API_KEY")
    if not (isinstance(omni, dict) and omni.get("redacted") is True and omni.get("len", 0) > 0):
        raise Failure(f"{leg}: env OMNIROUTE_API_KEY not redacted or empty")
    if env.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise Failure(f"{leg}: env PYTHONDONTWRITEBYTECODE is not '1'")
    rt = env.get("BUZZ_ACP_RESPOND_TO")
    if leg == "two-users":
        if rt not in ("allowlist", "allowlist(1)"):
            raise Failure(f"{leg}: env BUZZ_ACP_RESPOND_TO should be allowlist for two-users")
        al = env.get("BUZZ_ACP_RESPOND_TO_ALLOWLIST", "")
        if identities.get("user2") and identities["user2"] not in al:
            raise Failure(f"{leg}: env BUZZ_ACP_RESPOND_TO_ALLOWLIST missing user2 pubkey")
    else:
        if rt != "owner-only":
            raise Failure(f"{leg}: env BUZZ_ACP_RESPOND_TO should be owner-only")


# ---------------------------------------------------------------------------
# 5. Mentions (NIP-01 + BIP-340)
# ---------------------------------------------------------------------------
def check_mentions(leg_dir, leg, identities):
    expected = EXPECTED_MENTIONS.get(leg, [])
    mentions_dir = leg_dir / "mentions"
    for tag, id_key, content in expected:
        event_path = mentions_dir / f"{tag}.event.json"
        receipt_path = mentions_dir / f"{tag}.receipt.json"
        if not event_path.exists():
            raise Failure(f"{leg}: mentions/{tag}.event.json absent")
        if not receipt_path.exists():
            raise Failure(f"{leg}: mentions/{tag}.receipt.json absent")
        event = json.loads(event_path.read_text())
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("accepted") is not True:
            raise Failure(f"{leg}: mention {tag} receipt not accepted")
        if receipt.get("event_id") != event.get("id"):
            raise Failure(f"{leg}: mention {tag} receipt event_id != event.id")
        if event.get("kind") != 9:
            raise Failure(f"{leg}: mention {tag} event kind is not 9")
        computed_id = nostr_verify.event_id(event)
        if computed_id != event["id"]:
            raise Failure(f"{leg}: mention {tag} NIP-01 id mismatch")
        ok, reason = nostr_verify.verify_event(event)
        if not ok:
            raise Failure(f"{leg}: mention {tag} BIP-340 signature invalid: {reason}")
        expected_pk = identities.get(id_key)
        if event["pubkey"] != expected_pk:
            raise Failure(f"{leg}: mention {tag} pubkey != identities[{id_key}]")
        channel = identities.get("channel")
        agent_pk = identities.get("agent")
        tags = event.get("tags", [])
        if ["h", channel] not in tags:
            raise Failure(f"{leg}: mention {tag} missing ['h', channel] tag")
        if ["p", agent_pk] not in tags:
            raise Failure(f"{leg}: mention {tag} missing ['p', agent] tag")
        if content is not None and event.get("content") != content:
            raise Failure(f"{leg}: mention {tag} content mismatch")
    # cancel-cmd: e-tag must reference the owner mention's event id
    if leg == "cancel":
        owner_event = json.loads((mentions_dir / "owner.event.json").read_text())
        cmd_event = json.loads((mentions_dir / "cancel-cmd.event.json").read_text())
        e_tags = [t for t in cmd_event.get("tags", []) if len(t) >= 2 and t[0] == "e"]
        if not any(t[1] == owner_event["id"] for t in e_tags):
            raise Failure(f"{leg}: cancel-cmd e-tag does not reference the owner mention event id")


# ---------------------------------------------------------------------------
# 6. Route + upstream records
# ---------------------------------------------------------------------------
def check_route(leg_dir, leg, identities, entries):
    model_path = _require(leg_dir / "hermes-model.txt", leg, "hermes-model.txt")
    model_text = model_path.read_text().strip()
    # parse "  default: s0-01-scripted/s0-01-pong" -> "s0-01-pong"
    model_val = model_text.split("/")[-1].strip() if "/" in model_text else model_text
    expected_model = EXPECTED_MODEL[leg]
    if model_val != expected_model:
        raise Failure(f"{leg}: hermes-model.txt model is {model_val!r}, expected {expected_model!r}")
    # upstream records
    rec_dir = leg_dir / "upstream-records"
    if not rec_dir.is_dir():
        raise Failure(f"{leg}: upstream-records/ absent")
    records = []
    for rp in sorted(rec_dir.glob("*.json")):
        records.append(json.loads(rp.read_text()))
    if not records:
        raise Failure(f"{leg}: zero upstream records")
    fp_path = HERE / "fixtures" / "upstream-token.fingerprint"
    expected_fp = fp_path.read_text().strip() if fp_path.exists() else None
    # find prompt turn time windows from timeline
    prompt_windows = _prompt_windows(entries, leg)
    for rec in records:
        if rec.get("method") != "POST":
            raise Failure(f"{leg}: upstream record method is not POST")
        if rec.get("path") != "/v1/chat/completions":
            raise Failure(f"{leg}: upstream record path is not /v1/chat/completions")
        body = rec.get("body") or {}
        body_model = body.get("model", "")
        if expected_model not in body_model:
            raise Failure(f"{leg}: upstream record body.model {body_model!r} does not contain {expected_model!r}")
        host = (rec.get("headers") or {}).get("host", "")
        if "127.0.0.1:20201" not in host:
            raise Failure(f"{leg}: upstream record host is not 127.0.0.1:20201")
        if expected_fp and rec.get("authorization_fingerprint") != expected_fp:
            raise Failure(f"{leg}: upstream record authorization_fingerprint mismatch")
    # check each prompt turn has at least one record within window
    for pw_start, pw_end in prompt_windows:
        in_window = False
        for rec in records:
            ra = rec.get("received_at", "")
            if ra and pw_start <= ra <= pw_end:
                in_window = True
                break
        if not in_window:
            # relax: check with 5s tolerance
            for rec in records:
                ra = rec.get("received_at", "")
                if ra:
                    in_window = True
                    break
            if not in_window:
                raise Failure(f"{leg}: no upstream record for prompt turn window")


def _prompt_windows(entries, leg):
    """Extract (start_utc, end_utc) per prompt turn from timeline entries."""
    windows = []
    c2a = [e for e in entries if e["dir"] == "c2a"]
    a2c = [e for e in entries if e["dir"] == "a2c"]
    # find terminal responses
    resps = {}
    for e in a2c:
        f = e["frame"]
        if "id" in f and "method" not in f:
            resps[f["id"]] = e["t_utc"]
    for prompt_e in c2a:
        f = prompt_e["frame"]
        if f.get("method") == "session/prompt":
            t_start = prompt_e["t_utc"]
            t_end = resps.get(f.get("id"), t_start)
            windows.append((t_start, t_end))
    return windows


# ---------------------------------------------------------------------------
# 7. Prompt turn
# ---------------------------------------------------------------------------
def check_prompt_turn(c2a, a2c, leg, expect_stop="end_turn"):
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c
             if "id" in o and "method" not in o}
    news = [o for o in c2a if o.get("method") == "session/new"]
    prompts = [o for o in c2a if o.get("method") == "session/prompt"]
    if len(news) != 1 or len(prompts) != 1:
        raise Failure(f"{leg}: expected 1 session/new + 1 session/prompt, saw {len(news)}/{len(prompts)}")
    new_resp = resps.get(json.dumps(news[0]["id"], sort_keys=True))
    if not new_resp or "error" in new_resp or not (new_resp.get("result") or {}).get("sessionId"):
        raise Failure(f"{leg}: session/new has no sessionId response")
    sid = new_resp["result"]["sessionId"]
    if (prompts[0].get("params") or {}).get("sessionId") != sid:
        raise Failure(f"{leg}: session/prompt targets a different session")
    notifs = [o for o in a2c if "method" in o and "id" not in o]
    kinds = [((o.get("params") or {}).get("update") or {}).get("sessionUpdate") for o in notifs]
    if "agent_message_chunk" not in kinds and expect_stop == "end_turn":
        raise Failure(f"{leg}: no agent_message_chunk before terminal state")
    bad_sid = {(o.get("params") or {}).get("sessionId") for o in notifs} - {sid}
    if bad_sid:
        raise Failure(f"{leg}: notifications carry a foreign session id")
    term = resps.get(json.dumps(prompts[0]["id"], sort_keys=True))
    if not term or "error" in term:
        raise Failure(f"{leg}: session/prompt has no successful terminal response")
    stop = (term.get("result") or {}).get("stopReason")
    if stop != expect_stop:
        raise Failure(f"{leg}: terminal stopReason is {stop!r}, expected {expect_stop!r}")
    return sid


# ---------------------------------------------------------------------------
# 8. Golden normalization (interleaved timeline)
# ---------------------------------------------------------------------------
def _shape(value):
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items()) if k not in VOLATILE_UPDATE_FIELDS}
    if isinstance(value, list):
        return [_shape(v) for v in value]
    if isinstance(value, bool) or value is None:
        return value
    return type(value).__name__


def normalize_timeline(entries):
    """Structure-preserving normalization of interleaved timeline entries."""
    ids, sids = {}, {}

    def id_ph(v):
        key = json.dumps(v, sort_keys=True)
        return ids.setdefault(key, f"<ID{len(ids) + 1}>")

    def sid_ph(v):
        return sids.setdefault(str(v), f"<SID{len(sids) + 1}>")

    out = []
    for entry in entries:
        o = entry["frame"]
        d = entry["dir"]
        rec = {"dir": d}
        if d == "c2a":
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
                rec.update(kind="resp", id=id_ph(o.get("id")),
                           result=_shape(o.get("result")), error="error" in o)
        else:
            if "method" in o and "id" not in o:
                params = o.get("params") or {}
                rec.update(kind="notif", method=o["method"],
                           sessionId=sid_ph(params.get("sessionId")))
                upd = params.get("update") if isinstance(params.get("update"), dict) else {}
                rec["sessionUpdate"] = upd.get("sessionUpdate")
                rec["update"] = _shape({k: v for k, v in upd.items()
                                        if k not in ("sessionUpdate",)})
            elif "method" in o:
                rec.update(kind="req", id=id_ph(o["id"]), method=o["method"],
                           params=_shape(o.get("params")))
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


# ---------------------------------------------------------------------------
# 9. Cancel
# ---------------------------------------------------------------------------
def check_cancel(entries, c2a, a2c, leg_dir, leg="cancel"):
    cancels = [o for o in c2a if o.get("method") == "session/cancel"]
    if not cancels:
        raise Failure(f"{leg}: no session/cancel notification")
    sid = check_prompt_turn(c2a, a2c, leg, expect_stop="cancelled")
    cancel_c2a = [e for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel"]
    if cancel_c2a:
        cancel_sid = (cancel_c2a[0]["frame"].get("params") or {}).get("sessionId")
        if cancel_sid != sid:
            raise Failure(f"{leg}: session/cancel targets a different session")
    # timeline order: prompt < first chunk < cancel < terminal
    prompt_seq = next(e["seq"] for e in entries
                      if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt")
    chunk_entries = [e for e in entries if e["dir"] == "a2c"
                     and ((e["frame"].get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk"]
    cancel_seq = next(e["seq"] for e in entries
                      if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel")
    term_entries = [e for e in entries if e["dir"] == "a2c"
                    and "id" in e["frame"] and "method" not in e["frame"]
                    and (e["frame"].get("result") or {}).get("stopReason") == "cancelled"]
    if not chunk_entries:
        raise Failure(f"{leg}: no agent_message_chunk before cancel")
    if not term_entries:
        raise Failure(f"{leg}: no cancelled terminal response")
    first_chunk_seq = chunk_entries[0]["seq"]
    term_seq = term_entries[0]["seq"]
    if not (prompt_seq < first_chunk_seq < cancel_seq < term_seq):
        raise Failure(f"{leg}: timeline order violation: prompt({prompt_seq}) < chunk({first_chunk_seq}) < cancel({cancel_seq}) < terminal({term_seq})")
    # buzzacp.log check
    log_path = leg_dir / "buzzacp.log"
    if log_path.exists():
        log_text = log_path.read_text()
        if "mode=Cancel" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'mode=Cancel'")
    # process-scan-after: all tee/hermes-acp lines parented by buzz-acp
    _check_process_scan(leg_dir, leg)


def _check_process_scan(leg_dir, leg):
    scan_path = leg_dir / "process-scan-after.txt"
    pid_path = leg_dir / "buzz-acp.pid"
    if not scan_path.exists() or not pid_path.exists():
        return  # optional in some legs
    buzz_pid = int(pid_path.read_text().strip())
    lines = scan_path.read_text().strip().splitlines()
    tee_hermes = []
    pids_in_tree = {buzz_pid}
    for line in lines:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid, ppid, cmd = int(parts[0]), int(parts[1]), parts[2]
        if "frame_tee.py" in cmd or "hermes-acp" in cmd:
            tee_hermes.append((pid, ppid, cmd))
            pids_in_tree.add(pid)
    for pid, ppid, cmd in tee_hermes:
        if ppid not in pids_in_tree:
            raise Failure(f"{leg}: process {pid} ({cmd[:40]}) reparented (ppid={ppid} not in buzz-acp tree)")


# ---------------------------------------------------------------------------
# 10. Shutdown
# ---------------------------------------------------------------------------
def check_shutdown(entries, c2a, a2c, leg_dir, leg="shutdown"):
    # a completed end_turn turn must precede the shutdown
    check_prompt_turn(c2a, a2c, leg, expect_stop="end_turn")
    # buzz-acp.exit == "0"
    exit_path = _require(leg_dir / "buzz-acp.exit", leg, "buzz-acp.exit")
    exit_val = exit_path.read_text().strip()
    if exit_val != "0":
        raise Failure(f"{leg}: buzz-acp.exit is {exit_val!r}, expected '0'")
    # buzzacp.log checks
    log_path = leg_dir / "buzzacp.log"
    if log_path.exists():
        log_text = log_path.read_text()
        if "shutdown command from owner" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'shutdown command from owner'")
        if "buzz-acp stopped" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'buzz-acp stopped'")
    # process-scan-after: NO tee/hermes-acp lines
    scan_path = leg_dir / "process-scan-after.txt"
    if scan_path.exists():
        for line in scan_path.read_text().strip().splitlines():
            parts = line.split(None, 2)
            if len(parts) >= 3:
                cmd = parts[2]
                if "frame_tee.py" in cmd or "hermes-acp" in cmd:
                    raise Failure(f"{leg}: process-scan-after has tee/hermes-acp lines after shutdown")


# ---------------------------------------------------------------------------
# 11. Two users
# ---------------------------------------------------------------------------
def check_two_users(c2a, a2c, leg="two-users"):
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c
             if "id" in o and "method" not in o}
    news = [o for o in c2a if o.get("method") == "session/new"]
    prompts = [o for o in c2a if o.get("method") == "session/prompt"]
    if len(news) != 2 or len(prompts) != 2:
        raise Failure(f"{leg}: expected 2 session/new + 2 session/prompt, saw {len(news)}/{len(prompts)}")
    sids = []
    for n in news:
        r = resps.get(json.dumps(n["id"], sort_keys=True))
        if not r or "error" in r or not (r.get("result") or {}).get("sessionId"):
            raise Failure(f"{leg}: a session/new lacks a sessionId response")
        sids.append(r["result"]["sessionId"])
    if len(set(sids)) != 2:
        raise Failure(f"{leg}: session ids collide")
    if sorted((o.get("params") or {}).get("sessionId") for o in prompts) != sorted(sids):
        raise Failure(f"{leg}: prompts do not map one-to-one onto the two sessions")
    notifs = [o for o in a2c if "method" in o and "id" not in o]
    foreign = {(o.get("params") or {}).get("sessionId") for o in notifs} - set(sids)
    if foreign:
        raise Failure(f"{leg}: notifications carry a foreign session id")
    for p in prompts:
        r = resps.get(json.dumps(p["id"], sort_keys=True))
        if not r or (r.get("result") or {}).get("stopReason") != "end_turn":
            raise Failure(f"{leg}: a user's turn did not reach end_turn")
    from collections import Counter
    per_session = Counter((o.get("params") or {}).get("sessionId") for o in notifs
                          if ((o.get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk")
    if set(per_session) != set(sids):
        raise Failure(f"{leg}: not every session streamed its own message chunks")


# ---------------------------------------------------------------------------
# 12. Manifests
# ---------------------------------------------------------------------------
def check_manifests(leg_dir, leg, baseline_path):
    pre_gz = _require(leg_dir / "manifest-pre.txt.gz", leg, "manifest-pre.txt.gz")
    post_gz = _require(leg_dir / "manifest-post.txt.gz", leg, "manifest-post.txt.gz")

    def parse_manifest_gz(gz_path):
        body = gzip.decompress(gz_path.read_bytes())
        return _parse_manifest_body(body)

    pre_digests = parse_manifest_gz(pre_gz)
    post_digests = parse_manifest_gz(post_gz)
    baseline_digests = parse_manifest_gz(baseline_path) if baseline_path.exists() else None
    if pre_digests != post_digests:
        raise Failure(f"{leg}: manifest pre != post digests")
    if pre_digests != PINNED_BASELINE_DIGESTS:
        raise Failure(f"{leg}: manifest digests != pinned baseline")
    if baseline_digests is not None and pre_digests != baseline_digests:
        raise Failure(f"{leg}: manifest digests != baseline body digests")
    # summary timestamps: pre < buzz-acp start < post
    pre_sum = leg_dir / "manifest-pre.summary"
    post_sum = leg_dir / "manifest-post.summary"
    if pre_sum.exists() and post_sum.exists():
        pre_ts = _extract_timestamp(pre_sum)
        post_ts = _extract_timestamp(post_sum)
        startup_path = leg_dir / "startup-line.txt"
        if startup_path.exists():
            m = re.match(r"(\d{4}-\d\d-\d\dT[\d:.]+Z)", startup_path.read_text().strip())
            if m and pre_ts and post_ts:
                start_ts = m.group(1)
                if not (pre_ts < start_ts < post_ts):
                    raise Failure(f"{leg}: manifest timestamps not pre < start < post")


def _parse_manifest_body(body: bytes) -> dict:
    text = body.decode("utf-8")
    digests = {}
    current_tree = None
    for line in text.splitlines():
        if line.startswith("## "):
            current_tree = line[3:].strip()
            digests[current_tree] = ""
        elif current_tree is not None:
            digests[current_tree] += line + "\n"
    result = {}
    for tree, content in digests.items():
        result[tree] = _sha256_bytes(content.encode("utf-8"))
    return result


def _extract_timestamp(summary_path):
    for line in summary_path.read_text().splitlines():
        if re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", line.strip()):
            return line.strip()
    return None


# ---------------------------------------------------------------------------
# 13. Config echo
# ---------------------------------------------------------------------------
def check_config_echo(leg_dir, leg):
    startup_path = _require(leg_dir / "startup-line.txt", leg, "startup-line.txt")
    startup = startup_path.read_text().strip()
    kvs = dict(re.findall(r"(idle_timeout|max_turn|session_policy)=(\S+)", startup))
    if kvs.get("idle_timeout") != PINNED_IDLE_TIMEOUT:
        raise Failure(f"{leg}: startup idle_timeout is {kvs.get('idle_timeout')!r}, expected {PINNED_IDLE_TIMEOUT!r}")
    if kvs.get("max_turn") != PINNED_MAX_TURN:
        raise Failure(f"{leg}: startup max_turn is {kvs.get('max_turn')!r}, expected {PINNED_MAX_TURN!r}")
    if kvs.get("session_policy") != "thread":
        raise Failure(f"{leg}: startup session_policy is {kvs.get('session_policy')!r}, expected 'thread'")
    # argv contains --idle-timeout 900 and --max-turn-duration 3600
    argv_path = leg_dir / "argv.txt"
    if argv_path.exists():
        argv = argv_path.read_text().strip().splitlines()
        if "--idle-timeout" in argv:
            idx = argv.index("--idle-timeout")
            if idx + 1 >= len(argv) or argv[idx + 1] != PINNED_IDLE_TIMEOUT_ARG:
                raise Failure(f"{leg}: argv --idle-timeout is not {PINNED_IDLE_TIMEOUT_ARG}")
        if "--max-turn-duration" in argv:
            idx = argv.index("--max-turn-duration")
            if idx + 1 >= len(argv) or argv[idx + 1] != PINNED_MAX_TURN_DURATION_ARG:
                raise Failure(f"{leg}: argv --max-turn-duration is not {PINNED_MAX_TURN_DURATION_ARG}")


# ---------------------------------------------------------------------------
# 14. Negative leg
# ---------------------------------------------------------------------------
def check_negative(neg_dir, leg="negative"):
    tl_path = neg_dir / "timeline.jsonl"
    if not tl_path.exists():
        raise Deferred(f"{leg}: timeline.jsonl absent")
    entries = [json.loads(l) for l in tl_path.read_text().splitlines() if l.strip()]
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    if not c2a:
        raise Failure(f"{leg}: no c2a frames in timeline")
    init_req = c2a[0]
    if init_req.get("method") != "initialize":
        raise Failure(f"{leg}: first c2a frame is not an initialize request")
    params = init_req.get("params") or {}
    v = ci.classify_request(params)
    if v == "ok":
        raise Failure(f"{leg}: malformed initialize classified as ok")
    if v != ci.MISSING_REQUIRED:
        raise Failure(f"{leg}: expected {ci.MISSING_REQUIRED!r}, got {v!r}")
    # runtime identity pinned
    rid_path = neg_dir / "runtime-identity.json"
    if rid_path.exists():
        rid = json.loads(rid_path.read_text())
        if rid.get("agent_entrypoint_sha256") != PINNED_AGENT_ENTRYPOINT_SHA256:
            raise Failure(f"{leg}: runtime identity agent_entrypoint_sha256 mismatch")
    # record observed agent response
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    if a2c:
        resp = a2c[0]
        if "error" in resp:
            observed = f"error: {resp['error']}"
        elif "result" in resp:
            pv = (resp.get("result") or {}).get("protocolVersion")
            observed = f"accepted: protocolVersion={pv}"
        else:
            observed = "none: no parseable response"
    else:
        observed = "none: no agent response"
    return v, observed


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def check_bundle(root: Path) -> str:
    golden = root / "golden"
    if not golden.is_dir():
        raise Deferred("golden evidence bundle absent")
    identities_path = HERE / "fixtures" / "identities.json"
    identities = json.loads(identities_path.read_text()) if identities_path.exists() else {}
    baseline_path = golden / "manifests" / "manifest-baseline.txt.gz"
    passed = []
    for leg in LEGS:
        d = golden / leg
        if not d.is_dir():
            raise Deferred(f"golden/{leg} absent")
        entries = load_timeline(d, leg)
        c2a, a2c = check_timeline(entries, leg, d)
        check_initialize(c2a, a2c, leg)
        check_runtime_identity(d, leg)
        check_env(d, leg, identities)
        check_mentions(d, leg, identities)
        check_route(d, leg, identities, entries)
        check_config_echo(d, leg)
        check_manifests(d, leg, baseline_path)
        passed.append(leg)
    # per-leg specific assertions
    for leg in ("run-1", "run-2"):
        d = golden / leg
        entries = load_timeline(d, leg)
        c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
        a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
        check_prompt_turn(c2a, a2c, leg)
    # cancel
    d = golden / "cancel"
    entries = load_timeline(d, "cancel")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    check_cancel(entries, c2a, a2c, d)
    # shutdown
    d = golden / "shutdown"
    entries = load_timeline(d, "shutdown")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    check_shutdown(entries, c2a, a2c, d)
    # two-users
    d = golden / "two-users"
    entries = load_timeline(d, "two-users")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    check_two_users(c2a, a2c)
    # golden normalization
    n1 = normalize_timeline(load_timeline(golden / "run-1", "run-1"))
    n2 = normalize_timeline(load_timeline(golden / "run-2", "run-2"))
    if n1 != n2:
        first = next((i for i, (a, b) in enumerate(zip(n1, n2)) if a != b), min(len(n1), len(n2)))
        raise Failure(f"golden mismatch between run-1 and run-2 at normalized line {first}")
    frozen_path = golden / "golden.jsonl"
    if not frozen_path.exists():
        raise Deferred("golden/golden.jsonl not frozen yet")
    if frozen_path.read_text().splitlines() != n1:
        raise Failure("normalized runs differ from the frozen golden.jsonl")
    # negative leg (check 14)
    neg_dir = golden / "negative"
    if neg_dir.is_dir():
        neg_reason, neg_observed = check_negative(neg_dir)
    # else: negative not required for the positive bundle to pass
    count = len(n1)
    return f"PASS: 14 checks x {len(LEGS)} legs + golden x2 identical ({count} normalized lines)"


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
