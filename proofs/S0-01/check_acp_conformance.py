"""S0-01 ACP conformance checker v2.1 — derives EVERYTHING from raw files, exact values.

Exit codes: 0 PASS / 1 `failure_reason: <leg>: <reason>` / 2 `deferred: <reason>`.
DEFERRAL RULE: exits 2 iff golden/ is absent or NO leg directory contains timeline.jsonl.
Once ANY leg carries a timeline, EVERY absence of a required file is a Failure, never a deferral.
"""
from __future__ import annotations

import gzip
import hashlib
import json

import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pins import (  # noqa: E402
    ALLOWED_UPSTREAM_GET,
    ENV_ALLOWLIST_KEY,
    EXPECTED_MENTIONS,
    EXPECTED_MODEL,
    LEGS,
    MANIFEST_TREES,
    MENTION_TEXT,
    MENTION_WINDOW_SLACK_S,
    PINNED_AGENT_CAPABILITIES,
    PINNED_AGENT_ENTRYPOINT_SHA256,
    PINNED_AGENT_INTERPRETER_REALPATH,
    PINNED_AGENT_INTERPRETER_SHA256,
    PINNED_AGENT_REALPATH,
    PINNED_BASELINE_DIGESTS,
    PINNED_BASELINE_GZ_SHA256,
    PINNED_BUZZ_ACP_EXE_REALPATH,
    PINNED_BUZZ_ACP_SHA256,
    PINNED_CLIENT_PROTOCOL_VERSION,
    PINNED_ENV_KEYS,
    PINNED_GOLDEN_SHA256,
    PINNED_HERMES_HOME,
    PINNED_HOME,
    PINNED_IDLE_TIMEOUT,
    PINNED_IDLE_TIMEOUT_ARG,
    PINNED_LAUNCH_ARGV,
    PINNED_MAX_TURN,
    PINNED_MAX_TURN_DURATION_ARG,
    PINNED_PATH,
    PINNED_RELAY_URL,
    PINNED_ROUTE_PREFIX,
    PINNED_SESSION_POLICY,
    PINNED_TEE_PATH,
    PINNED_UPSTREAM_HOST,
    REDACTED_ENV_KEY_RE,
    UPSTREAM_POST_PATH,
    UPSTREAM_WINDOW_SLACK_S,
)
import check_initialize as ci  # noqa: E402
sys.path.insert(0, str(HERE / "tools"))
import nostr_verify  # noqa: E402

VOLATILE_UPDATE_FIELDS = {"content", "text", "title", "rawInput", "rawOutput",
                          "locations", "_meta", "usage"}

EXPECTED_CHECK_SEQUENCE = [
    "check_timeline", "check_initialize_frames", "check_runtime_identity",
    "check_env", "check_mentions", "check_route",
    "check_prompt_turn", "check_config_echo", "check_manifests",
    "check_process_evidence", "check_buzzacp_log",
    "check_cancel", "check_shutdown", "check_two_users",
    "check_golden", "check_negative",
]


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


def _parse_utc(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def _parse_utc_summary(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _reject_nan(line: str, leg: str, seq_hint: int):
    def _raise(c):
        raise Failure(f"{leg}: NaN or Infinity in timeline at seq {seq_hint}")
    return json.loads(line, parse_constant=_raise)


def _require_file(path: Path, leg: str, name: str):
    if not path.exists():
        raise Failure(f"{leg}: {name} absent")
    return path


def _require_dir(path: Path, leg: str, name: str):
    if not path.is_dir():
        raise Failure(f"{leg}: {name} absent")
    return path


def check_timeline(entries, leg, leg_dir):
    if not entries:
        raise Failure(f"{leg}: timeline.jsonl is empty")
    valid_keys = {"seq", "dir", "t_utc", "t_mono_ns", "frame"}
    utc_re = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
    for i, e in enumerate(entries):
        ks = set(e.keys())
        if e.get("frame") is None:
            raise Failure(f"{leg}: non-JSON frame at seq {i + 1}")
        if ks != valid_keys:
            raise Failure(f"{leg}: timeline entry at seq {i + 1} has unexpected keys {sorted(ks)}")
        seq_val = e["seq"]
        if not isinstance(seq_val, int) or isinstance(seq_val, bool):
            raise Failure(f"{leg}: timeline seq at index {i} is not int")
        if seq_val != i + 1:
            raise Failure(f"{leg}: timeline seq not strictly 1..N at index {i}")
        mono = e["t_mono_ns"]
        if not isinstance(mono, int) or isinstance(mono, bool):
            raise Failure(f"{leg}: timeline t_mono_ns at seq {seq_val} is not int")
        t_utc = e["t_utc"]
        if not isinstance(t_utc, str) or not utc_re.match(t_utc):
            raise Failure(f"{leg}: timeline t_utc at seq {seq_val} does not match format")
        _parse_utc(t_utc)
        d = e["dir"]
        if d not in ("c2a", "a2c"):
            raise Failure(f"{leg}: timeline dir at seq {seq_val} is {d!r}, expected 'c2a' or 'a2c'")
    for i in range(1, len(entries)):
        if entries[i]["t_mono_ns"] < entries[i - 1]["t_mono_ns"]:
            raise Failure(f"{leg}: t_mono_ns not non-decreasing at seq {entries[i]['seq']}")
    for i in range(1, len(entries)):
        if _parse_utc(entries[i]["t_utc"]) < _parse_utc(entries[i - 1]["t_utc"]):
            raise Failure(f"{leg}: t_utc not non-decreasing at seq {entries[i]['seq']}")
    c2a_split = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c_split = [e["frame"] for e in entries if e["dir"] == "a2c"]
    c2a_path = _require_file(leg_dir / "frames-client-to-agent.jsonl", leg, "frames-client-to-agent.jsonl")
    a2c_path = _require_file(leg_dir / "frames-agent-to-client.jsonl", leg, "frames-agent-to-client.jsonl")

    def _load_dir(fpath, name):
        raw = fpath.read_bytes()
        frames = []
        for lineno, lb in enumerate(raw.split(b"\n"), 1):
            if not lb or (lineno > 1 and not lb.strip()):
                continue
            if lb.endswith(b"\r"):
                lb = lb[:-1]
            try:
                text = lb.decode("utf-8")
            except UnicodeDecodeError:
                raise Failure(f"{leg}: {name} line {lineno} not valid UTF-8")
            try:
                frames.append(json.loads(text))
            except json.JSONDecodeError:
                raise Failure(f"{leg}: {name} line {lineno} not valid JSON")
        return frames

    c2a_file = _load_dir(c2a_path, "frames-client-to-agent.jsonl")
    a2c_file = _load_dir(a2c_path, "frames-agent-to-client.jsonl")
    if c2a_file != c2a_split:
        raise Failure(f"{leg}: frames-client-to-agent.jsonl does not match timeline c2a split")
    if a2c_file != a2c_split:
        raise Failure(f"{leg}: frames-agent-to-client.jsonl does not match timeline a2c split")
    return c2a_split, a2c_split


def check_initialize_frames(c2a, a2c, leg):
    init_reqs = [o for o in c2a if o.get("method") == "initialize"]
    if len(init_reqs) != 1:
        raise Failure(f"{leg}: expected one initialize request, got {len(init_reqs)}")
    req = init_reqs[0]
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c if "id" in o and "method" not in o}
    resp = resps.get(json.dumps(req["id"], sort_keys=True))
    if resp is None or "error" in resp:
        raise Failure(f"{leg}: initialize has no successful response")
    v = ci.classify_request(req["params"])
    if v != "ok":
        raise Failure(f"{leg}: initialize request {v}")
    v = ci.classify_response(resp["result"])
    if v != "ok":
        raise Failure(f"{leg}: initialize response {v}")
    if req["params"].get("protocolVersion") != PINNED_CLIENT_PROTOCOL_VERSION:
        raise Failure(f"{leg}: client protocolVersion is not {PINNED_CLIENT_PROTOCOL_VERSION}")
    if resp["result"].get("protocolVersion") != 1:
        raise Failure(f"{leg}: agent protocolVersion is not 1")
    if resp["result"].get("agentCapabilities") != PINNED_AGENT_CAPABILITIES:
        raise Failure(f"{leg}: agentCapabilities differ from pinned")


def check_runtime_identity(leg_dir, leg):
    rid = json.loads(_require_file(leg_dir / "runtime-identity.json", leg, "runtime-identity.json").read_text())

    def _chk(field, expected, desc=None):
        if rid.get(field) != expected:
            raise Failure(f"{leg}: {desc or field} mismatch")

    _chk("buzz_acp_exe_sha256", PINNED_BUZZ_ACP_SHA256)
    _chk("buzz_acp_exe_realpath", PINNED_BUZZ_ACP_EXE_REALPATH)
    _chk("agent_entrypoint_sha256", PINNED_AGENT_ENTRYPOINT_SHA256)
    _chk("agent_realpath", PINNED_AGENT_REALPATH)
    _chk("agent_argv", [PINNED_AGENT_REALPATH])
    _chk("agent_interpreter_realpath", PINNED_AGENT_INTERPRETER_REALPATH)
    _chk("agent_interpreter_sha256", PINNED_AGENT_INTERPRETER_SHA256)
    _chk("tee_path", PINNED_TEE_PATH)
    tee_file = HERE / "tools" / "frame_tee.py"
    if not tee_file.exists():
        raise Failure(f"{leg}: tools/frame_tee.py absent (needed for tee_sha256)")
    _chk("tee_sha256", _sha256_file(tee_file))
    if rid.get("python_dont_write_bytecode") is not True:
        raise Failure(f"{leg}: python_dont_write_bytecode is not true")
    pid_path = _require_file(leg_dir / "buzz-acp.pid", leg, "buzz-acp.pid")
    expected_pid = int(pid_path.read_text().strip())
    pid_val = rid.get("buzz_acp_pid")
    if not isinstance(pid_val, int) or isinstance(pid_val, bool) or pid_val != expected_pid:
        raise Failure(f"{leg}: buzz_acp_pid mismatch")
    argv_path = _require_file(leg_dir / "argv.txt", leg, "argv.txt")
    argv_lines = argv_path.read_text().splitlines()
    if argv_lines != PINNED_LAUNCH_ARGV:
        raise Failure(f"{leg}: argv.txt lines != PINNED_LAUNCH_ARGV")
    if rid.get("launch_argv") != PINNED_LAUNCH_ARGV:
        raise Failure(f"{leg}: launch_argv mismatch")


def check_env(leg_dir, leg, identities):
    env = json.loads(_require_file(leg_dir / "env.json", leg, "env.json").read_text())
    expected_keys = set(PINNED_ENV_KEYS)
    if leg == "two-users":
        expected_keys.add(ENV_ALLOWLIST_KEY)
    if set(env.keys()) != expected_keys:
        raise Failure(f"{leg}: env.json key set mismatch (extra={sorted(set(env.keys()) - expected_keys)}, missing={sorted(expected_keys - set(env.keys()))})")
    if leg != "two-users" and ENV_ALLOWLIST_KEY in env:
        raise Failure(f"{leg}: {ENV_ALLOWLIST_KEY} present in non-two-users leg")
    redact_re = re.compile(REDACTED_ENV_KEY_RE)
    hex64_re = re.compile(r"^[0-9a-f]{64}$")
    for key, val in env.items():
        if redact_re.search(key):
            if not isinstance(val, dict):
                raise Failure(f"{leg}: env {key} should be redacted but is not a dict")
            if val.get("redacted") is not True:
                raise Failure(f"{leg}: env {key} redacted is not true")
            length = val.get("len")
            if not isinstance(length, int) or isinstance(length, bool) or length <= 0:
                raise Failure(f"{leg}: env {key} redacted len is not a positive int")
            sha12 = val.get("sha256_12")
            if not isinstance(sha12, str) or not re.fullmatch(r"[0-9a-f]{12}", sha12):
                raise Failure(f"{leg}: env {key} sha256_12 is not 12 hex chars")
        else:
            if isinstance(val, dict):
                raise Failure(f"{leg}: env {key} is a dict but does not match redaction regex")
    if env.get("BUZZ_ACP_AGENT_OWNER") != identities["owner"]:
        raise Failure(f"{leg}: env BUZZ_ACP_AGENT_OWNER mismatch")
    if env.get("BUZZ_ACP_SESSION_POLICY") != PINNED_SESSION_POLICY:
        raise Failure(f"{leg}: env BUZZ_ACP_SESSION_POLICY mismatch")
    if env.get("HERMES_HOME") != PINNED_HERMES_HOME:
        raise Failure(f"{leg}: env HERMES_HOME mismatch")
    if env.get("BUZZ_RELAY_URL") != PINNED_RELAY_URL:
        raise Failure(f"{leg}: env BUZZ_RELAY_URL mismatch")
    if env.get("S0_01_AGENT") != PINNED_AGENT_REALPATH:
        raise Failure(f"{leg}: env S0_01_AGENT mismatch")
    if env.get("PATH") != PINNED_PATH:
        raise Failure(f"{leg}: env PATH mismatch")
    if env.get("HOME") != PINNED_HOME:
        raise Failure(f"{leg}: env HOME mismatch")
    if env.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise Failure(f"{leg}: env PYTHONDONTWRITEBYTECODE is not '1'")
    framedir = env.get("S0_01_FRAMEDIR")
    if not isinstance(framedir, str) or not framedir:
        raise Failure(f"{leg}: env S0_01_FRAMEDIR empty or missing")
    rt = env.get("BUZZ_ACP_RESPOND_TO")
    if leg == "two-users":
        if rt != "allowlist":
            raise Failure(f"{leg}: env BUZZ_ACP_RESPOND_TO should be 'allowlist' for two-users")
        if env.get(ENV_ALLOWLIST_KEY) != identities["user2"]:
            raise Failure(f"{leg}: env {ENV_ALLOWLIST_KEY} != identities.user2")
    else:
        if rt != "owner-only":
            raise Failure(f"{leg}: env BUZZ_ACP_RESPOND_TO should be owner-only")
    exempt_keys = {"BUZZ_ACP_AGENT_OWNER", ENV_ALLOWLIST_KEY}
    for key, val in env.items():
        if key in exempt_keys:
            continue
        if isinstance(val, str) and hex64_re.match(val):
            raise Failure(f"{leg}: env {key} contains a 64-hex string (possible secret leak)")


def check_mentions(leg_dir, leg, identities, entries):
    expected = EXPECTED_MENTIONS.get(leg, [])
    mentions_dir = _require_dir(leg_dir / "mentions", leg, "mentions/")
    expected_files = set()
    for tag, _, _, _ in expected:
        expected_files.update({f"{tag}.receipt.json", f"{tag}.event.json", f"{tag}.receipt.err"})
    actual_files = {f.name for f in mentions_dir.iterdir() if f.is_file()}
    extra = actual_files - expected_files
    if extra:
        raise Failure(f"{leg}: mentions/ has unexpected files: {sorted(extra)}")
    first_utc = _parse_utc(entries[0]["t_utc"])
    last_utc = _parse_utc(entries[-1]["t_utc"])
    event_ids = []
    for tag, id_key, content, replies_to in expected:
        event_path = _require_file(mentions_dir / f"{tag}.event.json", leg, f"mentions/{tag}.event.json")
        receipt_path = _require_file(mentions_dir / f"{tag}.receipt.json", leg, f"mentions/{tag}.receipt.json")
        err_path = _require_file(mentions_dir / f"{tag}.receipt.err", leg, f"mentions/{tag}.receipt.err")
        if err_path.read_text() != "":
            raise Failure(f"{leg}: mentions/{tag}.receipt.err is not empty")
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
        if event["pubkey"] != identities.get(id_key):
            raise Failure(f"{leg}: mention {tag} pubkey != identities[{id_key}]")
        tags = event.get("tags", [])
        if ["h", identities["channel"]] not in tags:
            raise Failure(f"{leg}: mention {tag} missing ['h', channel] tag")
        if ["p", identities["agent"]] not in tags:
            raise Failure(f"{leg}: mention {tag} missing ['p', agent] tag")
        if event.get("content") != content:
            raise Failure(f"{leg}: mention {tag} content mismatch")
        if replies_to is not None:
            ref_event = json.loads((mentions_dir / f"{replies_to}.event.json").read_text())
            e_tags = [t for t in tags if len(t) >= 2 and t[0] == "e"]
            if not any(t[1] == ref_event["id"] for t in e_tags):
                raise Failure(f"{leg}: mention {tag} e-tag does not reference {replies_to}")
        created_at = event.get("created_at")
        if not isinstance(created_at, int) or isinstance(created_at, bool):
            raise Failure(f"{leg}: mention {tag} created_at is not int")
        floor_first = int(first_utc.timestamp()) - MENTION_WINDOW_SLACK_S
        ceil_last = int(last_utc.timestamp()) + 1 + MENTION_WINDOW_SLACK_S
        if not (floor_first <= created_at <= ceil_last):
            raise Failure(f"{leg}: mention {tag} created_at {created_at} outside window [{floor_first}, {ceil_last}]")
        event_ids.append(event["id"])
    return event_ids


def check_route(leg_dir, leg, entries):
    model_path = _require_file(leg_dir / "hermes-model.txt", leg, "hermes-model.txt")
    model_text = model_path.read_text().strip()
    expected_model = EXPECTED_MODEL[leg]
    expected_model_text = f"default: {PINNED_ROUTE_PREFIX}/{expected_model}"
    if model_text != expected_model_text:
        raise Failure(f"{leg}: hermes-model.txt is {model_text!r}, expected {expected_model_text!r}")
    rec_dir = leg_dir / "upstream-records"
    if not rec_dir.is_dir():
        raise Failure(f"{leg}: zero upstream records / upstream-records/ absent")
    records = [json.loads(rp.read_text()) for rp in sorted(rec_dir.glob("*.json"))]
    if not records:
        raise Failure(f"{leg}: zero upstream records / upstream-records/ absent")
    fp_path = _require_file(HERE / "fixtures" / "upstream-token.fingerprint", leg, "fixtures/upstream-token.fingerprint")
    expected_fp = fp_path.read_text().strip()
    allowed_pairs = ALLOWED_UPSTREAM_GET | {("POST", UPSTREAM_POST_PATH)}
    for rec in records:
        mp = (rec.get("method"), rec.get("path"))
        if mp not in allowed_pairs:
            raise Failure(f"{leg}: upstream record ({mp[0]}, {mp[1]}) not in allowed set")
        host = (rec.get("headers") or {}).get("host", "")
        if host != PINNED_UPSTREAM_HOST:
            raise Failure(f"{leg}: upstream record host is {host!r}, expected {PINNED_UPSTREAM_HOST!r}")
    post_records = [r for r in records if r.get("method") == "POST"]
    for rec in post_records:
        if rec.get("authorization_fingerprint") != expected_fp:
            raise Failure(f"{leg}: upstream record authorization_fingerprint mismatch")
        body = rec.get("body") or {}
        if body.get("model") != expected_model:
            raise Failure(f"{leg}: upstream record body.model is {body.get('model')!r}, expected {expected_model!r}")
    prompt_windows = _prompt_windows(entries, leg)
    slack = timedelta(seconds=UPSTREAM_WINDOW_SLACK_S)
    for rec in post_records:
        ra_str = rec.get("received_at", "")
        if not ra_str:
            raise Failure(f"{leg}: upstream POST record missing received_at")
        ra = _parse_utc(ra_str)
        if not any(s - slack <= ra <= e + slack for s, e in prompt_windows):
            raise Failure(f"{leg}: upstream POST record received_at {ra_str} outside all prompt windows")
    for pw_start, pw_end in prompt_windows:
        found = False
        for rec in post_records:
            ra = _parse_utc(rec.get("received_at", "2000-01-01T00:00:00.000000Z"))
            if pw_start - slack <= ra <= pw_end + slack:
                body = rec.get("body") or {}
                if body.get("stream") is True:
                    for msg in body.get("messages", []):
                        if msg.get("role") == "user":
                            c = msg.get("content")
                            if isinstance(c, str) and MENTION_TEXT in c:
                                found = True
                            elif isinstance(c, list):
                                for part in c:
                                    if isinstance(part, dict) and MENTION_TEXT in str(part.get("text", "")):
                                        found = True
                        if found:
                            break
                if found:
                    break
        if not found:
            raise Failure(f"{leg}: no upstream POST with stream=true and mention text for a prompt window")


def _prompt_windows(entries, leg):
    resps = {}
    for e in entries:
        if e["dir"] == "a2c":
            f = e["frame"]
            if "id" in f and "method" not in f:
                resps[json.dumps(f["id"], sort_keys=True)] = _parse_utc(e["t_utc"])
    windows = []
    for e in entries:
        if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt":
            t_start = _parse_utc(e["t_utc"])
            t_end = resps.get(json.dumps(e["frame"].get("id"), sort_keys=True), t_start)
            windows.append((t_start, t_end))
    return windows


def check_prompt_turn(c2a, a2c, leg, entries, expect_stop="end_turn"):
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c if "id" in o and "method" not in o}
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
    prompt_seq = next(e["seq"] for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt")
    term_entries = [e for e in entries if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]
                    and json.dumps(e["frame"]["id"], sort_keys=True) == json.dumps(prompts[0]["id"], sort_keys=True)]
    if not term_entries:
        raise Failure(f"{leg}: session/prompt has no terminal response")
    term_seq = term_entries[0]["seq"]
    chunk_between = [e for e in entries if e["dir"] == "a2c" and prompt_seq < e["seq"] < term_seq
                     and ((e["frame"].get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk"]
    if not chunk_between:
        raise Failure(f"{leg}: no agent_message_chunk between prompt and terminal")
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


def _shape(value):
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items()) if k not in VOLATILE_UPDATE_FIELDS}
    if isinstance(value, list):
        return [_shape(v) for v in value]
    if isinstance(value, bool) or value is None:
        return value
    return type(value).__name__


def normalize_timeline(entries):
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
                elif o["method"] == "session/cancel":
                    rec["sessionId"] = sid_ph(params.get("sessionId"))
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


def check_cancel(entries, c2a, a2c, leg_dir, leg="cancel"):
    cancels = [o for o in c2a if o.get("method") == "session/cancel"]
    if not cancels:
        raise Failure(f"{leg}: no session/cancel notification")
    sid = check_prompt_turn(c2a, a2c, leg, entries, expect_stop="cancelled")
    cancel_c2a = [e for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel"]
    if cancel_c2a:
        cancel_sid = (cancel_c2a[0]["frame"].get("params") or {}).get("sessionId")
        if cancel_sid != sid:
            raise Failure(f"{leg}: session/cancel targets a different session")
    prompt_seq = next(e["seq"] for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt")
    chunk_entries = [e for e in entries if e["dir"] == "a2c"
                     and ((e["frame"].get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk"]
    cancel_seq = next(e["seq"] for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel")
    term_entries = [e for e in entries if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]
                    and (e["frame"].get("result") or {}).get("stopReason") == "cancelled"]
    if not chunk_entries:
        raise Failure(f"{leg}: no agent_message_chunk before cancel")
    if not term_entries:
        raise Failure(f"{leg}: no cancelled terminal response")
    first_chunk_seq = chunk_entries[0]["seq"]
    term_seq = term_entries[0]["seq"]
    if not (prompt_seq < first_chunk_seq < cancel_seq < term_seq):
        raise Failure(f"{leg}: timeline order violation: prompt({prompt_seq}) < chunk({first_chunk_seq}) < cancel({cancel_seq}) < terminal({term_seq})")


def check_shutdown(entries, c2a, a2c, leg_dir, leg="shutdown"):
    check_prompt_turn(c2a, a2c, leg, entries, expect_stop="end_turn")
    exit_path = _require_file(leg_dir / "buzz-acp.exit", leg, "buzz-acp.exit")
    exit_val = exit_path.read_text().strip()
    if exit_val != "0":
        raise Failure(f"{leg}: buzz-acp.exit is {exit_val!r}, expected '0'")


def check_two_users(c2a, a2c, entries, leg="two-users"):
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c if "id" in o and "method" not in o}
    news = [o for o in c2a if o.get("method") == "session/new"]
    prompts = [o for o in c2a if o.get("method") == "session/prompt"]
    if len(news) != 2 or len(prompts) != 2:
        raise Failure(f"{leg}: expected 2 session/new + 2 session/prompt, saw {len(news)}/{len(prompts)}")
    sids = []
    for n_obj in news:
        r = resps.get(json.dumps(n_obj["id"], sort_keys=True))
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
    for p_obj in prompts:
        r = resps.get(json.dumps(p_obj["id"], sort_keys=True))
        if not r or (r.get("result") or {}).get("stopReason") != "end_turn":
            raise Failure(f"{leg}: a user's turn did not reach end_turn")
    from collections import Counter
    per_session = Counter((o.get("params") or {}).get("sessionId") for o in notifs
                          if ((o.get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk")
    if set(per_session) != set(sids):
        raise Failure(f"{leg}: not every session streamed its own message chunks")


def check_manifests(leg_dir, leg, baseline_path, baseline_gz_sha):
    pre_gz = _require_file(leg_dir / "manifest-pre.txt.gz", leg, "manifest-pre.txt.gz")
    post_gz = _require_file(leg_dir / "manifest-post.txt.gz", leg, "manifest-post.txt.gz")
    pre_body = gzip.decompress(pre_gz.read_bytes())
    post_body = gzip.decompress(post_gz.read_bytes())
    _require_file(baseline_path, leg, "manifests/manifest-baseline.txt.gz")
    baseline_body = gzip.decompress(baseline_path.read_bytes())
    if _sha256_file(baseline_path) != baseline_gz_sha:
        raise Failure(f"{leg}: baseline gz sha256 mismatch")
    if pre_body != post_body:
        raise Failure(f"{leg}: manifest pre != post body")
    if pre_body != baseline_body:
        raise Failure(f"{leg}: manifest body != baseline body")
    pre_digests = _parse_manifest_body(pre_body, leg)
    if pre_digests != PINNED_BASELINE_DIGESTS:
        raise Failure(f"{leg}: manifest digests != pinned baseline")
    pre_sum = _require_file(leg_dir / "manifest-pre.summary", leg, "manifest-pre.summary")
    post_sum = _require_file(leg_dir / "manifest-post.summary", leg, "manifest-post.summary")
    pre_sum_d, pre_ts = _parse_summary(pre_sum, leg, "manifest-pre.summary")
    post_sum_d, post_ts = _parse_summary(post_sum, leg, "manifest-post.summary")
    if pre_sum_d != pre_digests:
        raise Failure(f"{leg}: manifest-pre.summary digests != body digests")
    if post_sum_d != pre_digests:
        raise Failure(f"{leg}: manifest-post.summary digests != body digests")
    rid = json.loads((leg_dir / "runtime-identity.json").read_text())
    start_dt = _parse_utc(rid["spawned_at_utc"])
    if not (pre_ts < start_dt < post_ts):
        raise Failure(f"{leg}: manifest timestamps not pre < start < post")
    tl_lines = [l for l in (leg_dir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    last_entry = json.loads(tl_lines[-1])
    if not (post_ts > _parse_utc(last_entry["t_utc"])):
        raise Failure(f"{leg}: manifest-post timestamp not after last timeline t_utc")


def _parse_manifest_body(body: bytes, leg: str) -> dict:
    text = body.decode("utf-8")
    lines = text.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    digests = {}
    current_tree = None
    tree_order = []
    for line in lines:
        if line.startswith("## "):
            tree_name = line[3:].strip()
            if tree_name in digests:
                raise Failure(f"{leg}: duplicate manifest header '## {tree_name}'")
            current_tree = tree_name
            tree_order.append(tree_name)
            digests[tree_name] = ""
        elif current_tree is not None:
            digests[current_tree] += line + "\n"
        else:
            raise Failure(f"{leg}: manifest body has content before first header")
    if not tree_order or tree_order[0] != "hermes-agent":
        raise Failure(f"{leg}: manifest first header is not '## hermes-agent'")
    if tuple(tree_order) != MANIFEST_TREES:
        raise Failure(f"{leg}: manifest tree order {tree_order} != {list(MANIFEST_TREES)}")
    return {tree: _sha256_bytes(content.encode("utf-8")) for tree, content in digests.items()}


def _parse_summary(summary_path, leg, name):
    lines = summary_path.read_text().splitlines()
    if len(lines) != 4:
        raise Failure(f"{leg}: {name} has {len(lines)} lines, expected 4")
    digests = {}
    for i, tree_name in enumerate(MANIFEST_TREES):
        parts = lines[i].split()
        if len(parts) != 2 or parts[0] != tree_name:
            raise Failure(f"{leg}: {name} format error at line {i + 1}")
        digests[tree_name] = parts[1]
    return digests, _parse_utc_summary(lines[3].strip())


def check_config_echo(leg_dir, leg):
    startup_path = _require_file(leg_dir / "startup-line.txt", leg, "startup-line.txt")
    startup = startup_path.read_text().strip()
    m = re.match(r'^(\S+)\s+INFO buzz_acp: buzz-acp starting: (.*)$', startup)
    if not m:
        raise Failure(f"{leg}: startup-line.txt does not match expected format")
    tokens = m.group(2).split(" ")
    required_keys = {"relay", "agent_cmd", "mcp_cmd", "idle_timeout", "max_turn",
                     "agents", "session_policy", "ignore_self", "permission_mode", "respond_to"}
    kvs = {}
    for token in tokens:
        if "=" not in token:
            continue
        key, _, val = token.partition("=")
        if key in required_keys:
            if key in kvs:
                raise Failure(f"{leg}: startup-line duplicate key {key!r}")
            kvs[key] = val
    missing = required_keys - set(kvs.keys())
    if missing:
        raise Failure(f"{leg}: startup-line missing keys: {sorted(missing)}")
    checks = {"relay": PINNED_RELAY_URL, "agent_cmd": PINNED_TEE_PATH, "mcp_cmd": "",
              "idle_timeout": PINNED_IDLE_TIMEOUT, "max_turn": PINNED_MAX_TURN, "agents": "1",
              "session_policy": PINNED_SESSION_POLICY, "ignore_self": "true",
              "permission_mode": "bypassPermissions"}
    for k, exp in checks.items():
        if kvs[k] != exp:
            raise Failure(f"{leg}: startup {k} is {kvs[k]!r}, expected {exp!r}")
    expected_rt = "owner-only" if leg != "two-users" else "allowlist(1)"
    if kvs["respond_to"] != expected_rt:
        raise Failure(f"{leg}: startup respond_to is {kvs['respond_to']!r}, expected {expected_rt!r}")
    argv_path = _require_file(leg_dir / "argv.txt", leg, "argv.txt")
    argv = argv_path.read_text().splitlines()
    if "--idle-timeout" not in argv:
        raise Failure(f"{leg}: argv.txt missing --idle-timeout")
    idx = argv.index("--idle-timeout")
    if idx + 1 >= len(argv) or argv[idx + 1] != PINNED_IDLE_TIMEOUT_ARG:
        raise Failure(f"{leg}: argv --idle-timeout is not {PINNED_IDLE_TIMEOUT_ARG}")
    if "--max-turn-duration" not in argv:
        raise Failure(f"{leg}: argv.txt missing --max-turn-duration")
    idx = argv.index("--max-turn-duration")
    if idx + 1 >= len(argv) or argv[idx + 1] != PINNED_MAX_TURN_DURATION_ARG:
        raise Failure(f"{leg}: argv --max-turn-duration is not {PINNED_MAX_TURN_DURATION_ARG}")


def check_process_evidence(leg_dir, leg):
    pid_path = _require_file(leg_dir / "buzz-acp.pid", leg, "buzz-acp.pid")
    try:
        buzz_pid = int(pid_path.read_text().strip())
    except ValueError:
        raise Failure(f"{leg}: buzz-acp.pid is not a valid integer")
    if leg == "shutdown":
        scan_path = _require_file(leg_dir / "process-scan-after.txt", leg, "process-scan-after.txt")
        for line in scan_path.read_text().strip().splitlines():
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            cmd = parts[2]
            if PINNED_TEE_PATH in cmd or PINNED_AGENT_REALPATH in cmd or PINNED_BUZZ_ACP_EXE_REALPATH in cmd:
                raise Failure(f"{leg}: process-scan-after has tee/hermes-acp lines after shutdown")
    else:
        scan_path = _require_file(leg_dir / "process-scan-after.txt", leg, "process-scan-after.txt")
        all_procs = []
        for line in scan_path.read_text().strip().splitlines():
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            try:
                pid, ppid = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            all_procs.append((pid, ppid, parts[2]))
        pids_in_tree = {buzz_pid}
        changed = True
        while changed:
            changed = False
            for pid, ppid, cmd in all_procs:
                if ppid in pids_in_tree and pid not in pids_in_tree:
                    pids_in_tree.add(pid)
                    changed = True
        buzz_found = any(pid == buzz_pid and cmd.startswith(PINNED_BUZZ_ACP_EXE_REALPATH) for pid, _, cmd in all_procs)
        if not buzz_found:
            raise Failure(f"{leg}: process-scan-after has no buzz-acp line with pid {buzz_pid}")
        tee_pids = {pid for pid, ppid, cmd in all_procs if PINNED_TEE_PATH in cmd and ppid == buzz_pid}
        if not tee_pids:
            raise Failure(f"{leg}: no tee process parented by buzz-acp")
        if not any(PINNED_AGENT_REALPATH in cmd and ppid in tee_pids for _, ppid, cmd in all_procs):
            raise Failure(f"{leg}: no agent process parented by a tee process")
        for pid, ppid, cmd in all_procs:
            if PINNED_TEE_PATH in cmd or PINNED_AGENT_REALPATH in cmd or PINNED_BUZZ_ACP_EXE_REALPATH in cmd:
                if "pc_launch.py" in cmd:
                    continue
                if pid not in pids_in_tree:
                    raise Failure(f"{leg}: process {pid} ({cmd[:40]}) not in buzz-acp descendant tree")
        teardown_path = _require_file(leg_dir / "process-scan-teardown.txt", leg, "process-scan-teardown.txt")
        for line in teardown_path.read_text().strip().splitlines():
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            if PINNED_TEE_PATH in parts[2] or PINNED_AGENT_REALPATH in parts[2] or PINNED_BUZZ_ACP_EXE_REALPATH in parts[2]:
                raise Failure(f"{leg}: process-scan-teardown has tee/agent/buzz-acp lines after teardown")


def check_buzzacp_log(leg_dir, leg):
    log_path = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log")
    log_text = log_path.read_text()
    if re.search(r'[0-9a-f]{64}', log_text):
        raise Failure(f"{leg}: buzzacp.log contains unmasked 64-hex string")
    if leg == "cancel":
        if "mode=Cancel" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'mode=Cancel'")
    elif leg == "shutdown":
        if "shutdown command from owner" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'shutdown command from owner'")
        if "buzz-acp stopped" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'buzz-acp stopped'")


def check_negative(neg_dir, leg="negative"):
    tl_path = neg_dir / "timeline.jsonl"
    if not tl_path.exists():
        raise Failure(f"{leg}: timeline.jsonl absent")
    entries = [json.loads(l) for l in tl_path.read_text().splitlines() if l.strip()]
    c2a = [e for e in entries if e["dir"] == "c2a"]
    if not c2a:
        raise Failure(f"{leg}: no c2a frames in timeline")
    init_req = c2a[0]["frame"]
    if init_req.get("method") != "initialize":
        raise Failure(f"{leg}: first c2a frame is not an initialize request")
    fixture_path = HERE / "fixtures" / "neg-malformed-initialize.json"
    if fixture_path.exists():
        if init_req.get("params") != json.loads(fixture_path.read_text()):
            raise Failure(f"{leg}: initialize params != fixture")
    params = init_req.get("params") or {}
    v = ci.classify_request(params)
    if v == "ok":
        raise Failure(f"{leg}: malformed initialize classified as ok")
    if v != ci.MISSING_REQUIRED:
        raise Failure(f"{leg}: expected {ci.MISSING_REQUIRED!r}, got {v!r}")
    rid_path = neg_dir / "runtime-identity.json"
    if rid_path.exists():
        rid = json.loads(rid_path.read_text())
        for field, pin in [("agent_realpath", PINNED_AGENT_REALPATH),
                           ("agent_entrypoint_sha256", PINNED_AGENT_ENTRYPOINT_SHA256),
                           ("agent_interpreter_realpath", PINNED_AGENT_INTERPRETER_REALPATH),
                           ("agent_interpreter_sha256", PINNED_AGENT_INTERPRETER_SHA256)]:
            if rid.get(field) != pin:
                raise Failure(f"{leg}: runtime identity {field} mismatch")
        if rid.get("python_dont_write_bytecode") is not True:
            raise Failure(f"{leg}: runtime identity python_dont_write_bytecode is not true")
    env_path = neg_dir / "env.json"
    if env_path.exists():
        neg_env = json.loads(env_path.read_text())
        if neg_env.get("HERMES_HOME") != PINNED_HERMES_HOME:
            raise Failure(f"{leg}: env HERMES_HOME mismatch")
        if neg_env.get("PYTHONDONTWRITEBYTECODE") != "1":
            raise Failure(f"{leg}: env PYTHONDONTWRITEBYTECODE is not '1'")
    a2c = [e for e in entries if e["dir"] == "a2c"]
    if not a2c:
        raise Failure(f"{leg}: no agent response captured")
    resp = a2c[0]["frame"]
    if resp is None:
        observed = "none: no parseable response"
    elif "error" in resp:
        err = resp["error"]
        code = err.get("code", "?") if isinstance(err, dict) else "?"
        message = err.get("message", "?") if isinstance(err, dict) else str(err)
        observed = f"error code={code} message={message}"
    elif "result" in resp:
        res = resp.get("result") or {}
        pv = res.get("protocolVersion")
        ac = json.dumps(res.get("agentCapabilities"), sort_keys=True, separators=(",", ":")) if "agentCapabilities" in res else "null"
        observed = f"result protocolVersion={pv} agentCapabilities={ac}"
    else:
        observed = "none: no parseable response"
    return v, f"observed: {observed}"


def check_golden(golden_dir, leg="golden"):
    n1 = normalize_timeline(_load_timeline_raw(golden_dir / "run-1", "run-1"))
    n2 = normalize_timeline(_load_timeline_raw(golden_dir / "run-2", "run-2"))
    if n1 != n2:
        first = next((i for i, (a, b) in enumerate(zip(n1, n2)) if a != b), min(len(n1), len(n2)))
        raise Failure(f"{leg}: golden mismatch between run-1 and run-2 at normalized line {first}")
    frozen_path = _require_file(golden_dir / "golden.jsonl", leg, "golden.jsonl")
    frozen_bytes = frozen_path.read_bytes()
    frozen_sha = _sha256_bytes(frozen_bytes)
    if PINNED_GOLDEN_SHA256 is None:
        raise Failure(f"{leg}: golden not pinned")
    if frozen_sha != PINNED_GOLDEN_SHA256:
        raise Failure(f"{leg}: golden.jsonl sha256 {frozen_sha[:12]} != pinned {PINNED_GOLDEN_SHA256[:12]}")
    frozen_lines = [l for l in frozen_bytes.decode("utf-8").splitlines() if l.strip()]
    if frozen_lines != n1:
        raise Failure(f"{leg}: normalized runs differ from the frozen golden.jsonl")
    if not n1:
        raise Failure(f"{leg}: golden is empty")
    first_rec = json.loads(n1[0])
    if first_rec.get("dir") != "c2a" or first_rec.get("method") != "initialize":
        raise Failure(f"{leg}: first normalized line is not c2a initialize request")
    if first_rec.get("protocolVersion") != PINNED_CLIENT_PROTOCOL_VERSION:
        raise Failure(f"{leg}: first normalized line protocolVersion is not {PINNED_CLIENT_PROTOCOL_VERSION}")
    last_rec = json.loads(n1[-1])
    if last_rec.get("stopReason") != "end_turn":
        raise Failure(f"{leg}: last normalized line is not end_turn terminal")
    run1_entries = _load_timeline_raw(golden_dir / "run-1", "run-1")
    run2_entries = _load_timeline_raw(golden_dir / "run-2", "run-2")

    def _raw_sid(ents):
        for e in ents:
            if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
                r = e["frame"].get("result") or {}
                if "sessionId" in r:
                    return r["sessionId"]
        return None

    sid1, sid2 = _raw_sid(run1_entries), _raw_sid(run2_entries)
    if sid1 is not None and sid2 is not None and sid1 == sid2:
        raise Failure(f"{leg}: run-1 and run-2 raw sessionIds are identical")
    if run1_entries[0]["t_utc"] == run2_entries[0]["t_utc"]:
        raise Failure(f"{leg}: run-1 and run-2 first t_utc are identical")
    r1m = golden_dir / "run-1" / "mentions" / "owner.event.json"
    r2m = golden_dir / "run-2" / "mentions" / "owner.event.json"
    if r1m.exists() and r2m.exists():
        if json.loads(r1m.read_text()).get("id") == json.loads(r2m.read_text()).get("id"):
            raise Failure(f"{leg}: run-1 and run-2 owner mention event ids are identical")
    return n1


def _load_timeline_raw(leg_dir, leg):
    tl_path = leg_dir / "timeline.jsonl"
    return [_reject_nan(line, leg, i + 1) for i, line in enumerate(tl_path.read_text().splitlines()) if line.strip()]


def check_bundle(root: Path) -> str:
    golden = root / "golden"
    if not golden.is_dir():
        raise Deferred("golden evidence bundle absent")
    has_any_timeline = any((golden / leg / "timeline.jsonl").exists() for leg in LEGS)
    if not has_any_timeline:
        raise Deferred("v2 evidence not captured")
    identities_path = HERE / "fixtures" / "identities.json"
    _require_file(identities_path, "golden", "fixtures/identities.json")
    identities = json.loads(identities_path.read_text())
    baseline_path = golden / "manifests" / "manifest-baseline.txt.gz"
    expected_dirs = set(LEGS) | {"negative", "manifests"}
    expected_files = {"golden.jsonl"}
    for item in golden.iterdir():
        if item.is_dir() and item.name not in expected_dirs:
            raise Failure(f"golden: unexpected directory golden/{item.name}")
        if item.is_file() and item.name not in expected_files:
            raise Failure(f"golden: unexpected file golden/{item.name}")
    executed = []
    all_mention_event_ids = []
    for leg in LEGS:
        d = golden / leg
        if not d.is_dir():
            raise Failure(f"golden: golden/{leg} absent")
        entries = _load_timeline_raw(d, leg)
        c2a_split, a2c_split = check_timeline(entries, leg, d)
        check_initialize_frames(c2a_split, a2c_split, leg)
        check_runtime_identity(d, leg)
        check_env(d, leg, identities)
        leg_event_ids = check_mentions(d, leg, identities, entries)
        all_mention_event_ids.extend(leg_event_ids)
        check_route(d, leg, entries)
    executed.extend(["check_timeline", "check_initialize_frames", "check_runtime_identity",
                     "check_env", "check_mentions", "check_route"])
    for leg in ("run-1", "run-2", "shutdown"):
        d = golden / leg
        entries = _load_timeline_raw(d, leg)
        c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
        a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
        check_prompt_turn(c2a, a2c, leg, entries)
    executed.append("check_prompt_turn")
    for leg in LEGS:
        check_config_echo(golden / leg, leg)
    executed.append("check_config_echo")
    for leg in LEGS:
        check_manifests(golden / leg, leg, baseline_path, PINNED_BASELINE_GZ_SHA256)
    executed.append("check_manifests")
    for leg in LEGS:
        check_process_evidence(golden / leg, leg)
    executed.append("check_process_evidence")
    for leg in LEGS:
        check_buzzacp_log(golden / leg, leg)
    executed.append("check_buzzacp_log")
    d = golden / "cancel"
    entries = _load_timeline_raw(d, "cancel")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    check_cancel(entries, c2a, a2c, d)
    executed.append("check_cancel")
    d = golden / "shutdown"
    entries = _load_timeline_raw(d, "shutdown")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    check_shutdown(entries, c2a, a2c, d)
    executed.append("check_shutdown")
    d = golden / "two-users"
    entries = _load_timeline_raw(d, "two-users")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    check_two_users(c2a, a2c, entries)
    executed.append("check_two_users")
    if len(all_mention_event_ids) != len(set(all_mention_event_ids)):
        raise Failure("golden: mention event id replayed across legs")
    golden_lines = check_golden(golden)
    executed.append("check_golden")
    neg_dir = golden / "negative"
    _require_dir(neg_dir, "golden", "negative/")
    neg_reason, neg_observed = check_negative(neg_dir)
    executed.append("check_negative")
    if executed != EXPECTED_CHECK_SEQUENCE:
        raise Failure("golden: check sequence mismatch")
    count = len(golden_lines)
    golden_sha_12 = _sha256_bytes("\n".join(golden_lines).encode("utf-8") + b"\n")[:12]
    return (f"PASS: S0-01 acp-conformance — {len(executed)} checks executed over "
            f"{len(LEGS)} legs; golden x2 identical ({count} normalized lines, "
            f"sha256 {golden_sha_12}); {neg_observed}")


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
    except Exception as exc:
        print(f"failure_reason: malformed evidence: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
